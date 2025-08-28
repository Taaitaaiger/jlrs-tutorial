#!/usr/bin/env bash



scriptdir=$(dirname -- "$(realpath -- "$0")")
current_dir=$PWD

cd $scriptdir

if [ ! -d test_cases ]; then
    echo >&2 -e "\033[1;31mERROR: Test cases have not been generated yet, execute generate_tests.py\033[0m"
    exit 1
fi

if  [ -z "$JLRS_JULIA_DIR" -o ! -f "$JLRS_JULIA_DIR/bin/julia" ]; then
    if [ -z "$(which julia)" ]; then
        # Julia is neither installed nor provided via JLRS_JULIA_PATH
        echo >&2 -e "\033[1;31mERROR: \033[0;31mjulia executable not found\033[0m"
        exit 1
    elif [ ! -z "$(julia --help 2>&1 | grep juliaup)" ]; then
        # Julia is on PATH, but juliaup is used. 
        echo >&2 -e "\033[1;31mERROR: \033[0;31musing juliaup is not supported, set JLRS_JULIA_DIR\033[0m"
        exit 1
    else
        # Julia is on PATH, set as preferred version
        jlrs_julia_dir=$(dirname $(dirname $(which julia)))
        export JLRS_JULIA_DIR=$jlrs_julia_dir
    fi
fi

export LD_LIBRARY_PATH=$JLRS_JULIA_DIR/lib:$LD_LIBRARY_PATH

cd test_cases
test_cases=$(cargo read-manifest | jq '.targets[].name')

echo -e "\033[1;34mINFO: \033[0;34mBuild binary tests\033[0m"
cargo build --all >/dev/null 2>&1

echo -e "\033[1;34mINFO: \033[0;34mRun binary tests\033[0m"
n_failed=0
for case in $test_cases; do
    case=${case:1:-1}
    echo -e "\033[1;34mINFO: \033[0;34mRun $case\033[0m"
    script --flush --quiet --return /tmp/test_output --command "cargo run --bin $case 2>&1" 2>&1 >/dev/null
    if [ $? -eq 0 ]; then
        echo >&2 -e "\033[1;34mINFO: \033[0;34mTest $case succeeded\033[0m"
    else
        echo >&2 -e "\033[1;31mERROR: \033[0;31mTest $case failed\033[0m"
        out=$(sed '$d' /tmp/test_output | sed '$d' | sed '1d')
        echo -e "$out"
        failed_tests[$n_failed]="$case (bin)"
        n_failed=$((n_failed+1))
    fi
done

# Remove libtester before searching Cargo.toml files
if [ -d libtester ]; then
    rm -rf libtester
fi

lib_tomls=$(ls */Cargo.toml)

# Separate testing crate to avoid repeatedly compiling everything from scratch
cargo new --lib libtester 2>/dev/null
if [ $? -ne 0 ]; then
    echo >&2 -e "\033[1;31mERROR: \033[0;31mFailed to create libtester-crate\033[0m"
    exit 1
fi

cd libtester

for lib_toml in $lib_tomls; do
    lib_dir=${lib_toml::-11}
    echo -e "\033[1;34mINFO: \033[0;34mBuild $lib_dir\033[0m"
    cp ../$lib_dir/Cargo.toml .
    cp ../${lib_dir}/src/lib.rs src
    script --flush --quiet --return /tmp/test_output --command "cargo build 2>&1" 2>&1 >/dev/null

    if [ $? -eq 0 ]; then
        echo >&2 -e "\033[1;34mINFO: \033[0;34mSuccessfully built library test $lib_dir\033[0m"
    else
        echo >&2 -e "\033[1;31mERROR: \033[0;31mFailed to build library test $lib_dir\033[0m"
        out=$(sed '$d' /tmp/test_output | sed '$d' | sed '1d')
        failed_tests[$n_failed]="$lib_dir (lib)"
        n_failed=$((n_failed+1))
        echo -e "$out"
        continue
    fi   

    if [ -f ../$lib_dir/ModuleTest.jl ]; then
        cp ../$lib_dir/ModuleTest.jl .
        echo >&2 -e "\033[1;34mINFO: \033[0;34mRun library test module in $lib_dir\033[0m"
        $JLRS_JULIA_DIR/bin/julia ModuleTest.jl
        
        if [ $? -eq 0 ]; then
            echo >&2 -e "\033[1;34mINFO: \033[0;34mLibrary test $lib_dir succeeded\033[0m"
        else
            failed_tests[$n_failed]="$lib_dir (lib)"
            n_failed=$((n_failed+1))
            echo >&2 -e "\033[1;31mERROR: \033[0;31mLibrary test $lib_dir failed\033[0m"
        fi
    fi
done

if [ $n_failed -ne 0 ]; then
    echo >&2 -e "\033[1;31mERROR: \033[0;31mFailed tests:\033[0m"
    last=$((n_failed-1))
    for i in $(seq 0 $last); do
        echo >&2 -e "    \033[0;31m${failed_tests[$i]}\033[0m"
    done

    exit 1
fi

