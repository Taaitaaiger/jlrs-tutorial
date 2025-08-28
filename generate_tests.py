#! /usr/bin/env python3

import glob
import os
import subprocess
from pathlib import Path
import shutil
import logging
import sys


logger = logging.getLogger(__name__)

try:
    JLRS_PATH = sys.argv[1]
except:
    JLRS_PATH = None


def cargo_toml_bin_template(jlrs_path):
    if jlrs_path is not None:
        jlrs_path = f'path = "{jlrs_path}", '
    else:
        jlrs_path = ""
        
    return f"""[package]
name = "julia_app"
version = "0.1.0"
edition = "2024"

[features]

[profile.dev]
panic = "abort"

[profile.release]
panic = "abort"

[dependencies]
jlrs = {{version = "0.22", {jlrs_path}features = ["full", "ccall"]}}"""


def cargo_toml_lib_template(name, jlrs_path):
    if jlrs_path is not None:
        jlrs_path = f'path = "{jlrs_path}", '
    else:
        jlrs_path = ""
        
    return f"""[package]
name = "{name}"
version = "0.1.0"
edition = "2024"

[profile.dev]
panic = "abort"

[profile.release]
panic = "abort"

[features]

[lib]
crate-type = ["cdylib"]

[dependencies]
jlrs = {{ {jlrs_path}version = "0.22", features = ["jlrs-derive", "ccall", "complex"] }}"""


def bin_fragment(bin_name):
    return f"""
[[bin]]
name = "{bin_name}"
path = "src/{bin_name}.rs"
"""


def default_module_fragment(test_lib_path):
    return f"""module JuliaModuleTutorial
using JlrsCore.Wrap

@wrapmodule("{test_lib_path}", :julia_module_tutorial_init_fn)

function __init__()
    @initjlrs
end
end

"""


class TestCase:
    def __init__(self, file_name):
        self.rust_lines = []
        self.file_name = file_name
        self.generated = False

    def generate_name(self, idx):
        clean_name = (
            self.file_name.removeprefix("src/").removesuffix(".md").replace("/", "-")
        )

        name_offset = clean_name.find("-") + 1
        test_name = clean_name[name_offset:] + f"-{idx}"
        self.name = test_name.replace("-", "_")

    def append(self, line):
        self.rust_lines.append(line)


class DocTest(TestCase):
    def __init__(self, file_name):
        super().__init__(file_name)

    def generate(self, idx):
        self.generate_name(idx)
        logger.info(f"Generating bin test-case {self.name}")

        with open(f"src/{self.name}.rs", "w") as main_rs:
            main_rs.writelines(self.rust_lines)

        with open("Cargo.toml", "a") as cargo_toml:
            content = bin_fragment(self.name)
            cargo_toml.write(content)

        self.generated = True


def indented(prefix_len, lines):
    line_prefix = prefix_len * " "

    formatted_lines = [f"{line_prefix}{lines[0]}"]
    for line in lines[1:]:
        formatted_lines.append(f"{line_prefix}{line}")

    return formatted_lines


def adjust_spaces(lst, offset, n):
    prefix = " " * n
    return [prefix + line[offset:] for line in lst]


class LibTest(TestCase):
    def __init__(self, file_name):
        super().__init__(file_name)
        self.raw_julia_lines = []
        self.generated_julia_lines = []
        self.parsing_jl = False

    def set_parsing_julia(self):
        self.parsing_jl = True

    def append(self, line):
        if self.parsing_jl:
            self.raw_julia_lines.append(line)
        else:
            self.rust_lines.append(line)
            
    def _generate_call(self, cmd_lines):
        if len(cmd_lines) == 1:
            self.generated_julia_lines += [f'println("Call: {cmd_lines[0][:-1]}")\n']
        else:
            joined = "".join(adjust_spaces(cmd_lines[1:], 7, 6))
            self.generated_julia_lines += [f'println("Call: {cmd_lines[0][:-1]}\n{joined[:-1]}")\n']
            
    def _generate_result_assignment(self):
        pass
            
    def _generate_result(self, cmd_lines, result_lines, is_assignment, var_name):
        if len(cmd_lines) == 1:
            if is_assignment:
                self.generated_julia_lines += [
                    'print("Result: ")\n',
                    "try\n",
                    f"    global {cmd_lines[0][:-1]}\n",
                    f"    show({var_name})\n",
                    "catch e\n",
                    "    showerror(stdout, e, stacktrace(catch_backtrace()))\n",
                    "end\n",
                    "println()\n",
                ]
            else:
                if "print" in cmd_lines[0]:
                    show = f"    {cmd_lines[0][:-1]}\n"
                else:
                    show = f"    show({cmd_lines[0][:-1]})\n"

                self.generated_julia_lines += [
                    'print("Result: ")\n',
                    "try\n",
                    show,
                    "catch e\n",
                    "    showerror(stdout, e, stacktrace(catch_backtrace()))\n",
                    "end\n",
                    "println()\n",
                ]
        else:
            if is_assignment:
                joined = "".join(adjust_spaces(cmd_lines[1:], 7, 8))
                self.generated_julia_lines += [
                    'print("Result: ")\n',
                    "try\n",
                    f"    global {cmd_lines[0][:-1]}\n{joined[:-1]}\n",
                    f"    show({var_name})\n",
                    "catch e\n",
                    "    showerror(stdout, e, stacktrace(catch_backtrace()))\n",
                    "end\n",
                    "println()\n",
                ]
            else:
                joined = "".join(adjust_spaces(cmd_lines[1:], 7, 8))

                if "print" in cmd_lines[0] or "print" in joined:
                    show = [
                        f"   {cmd_lines[0][:-1]}\n{joined[:-1]}",
                    ]
                else:
                    show = [
                        "    show(\n",
                        f"       {cmd_lines[0][:-1]}\n{joined[:-1]}",
                        "    )",
                    ]

                self.generated_julia_lines += (
                    ['print("Result: ")\n', "try\n"]
                    + show
                    + [
                        "catch e\n",
                        "    showerror(stdout, e, stacktrace(catch_backtrace()))\n",
                        "end\n",
                        "println()\n",
                    ]
                )


    def _generate_expected(self, result_lines):
        if len(result_lines) == 1:
            self.generated_julia_lines += [f'println("Expected: {result_lines[0][:-1]}")\n']
        else:
            joined = "".join(adjust_spaces(result_lines[1:], 0, 0))
            self.generated_julia_lines += [f'println("Expected: {result_lines[0]}{joined[:-1]}")\n']


    def generate_julia_module_case(self, cmd_lines, result_lines):
        is_assignment = False
        var_name = None
        if "=" in cmd_lines[0]:
            var_name = cmd_lines[0].split("=")[0].strip()
            is_assignment = True

        self._generate_call(cmd_lines)
        self._generate_result(cmd_lines, result_lines, is_assignment, var_name)
        self._generate_expected(result_lines)

        return self.generated_julia_lines

    def prepare_julia_src(self):
        test_lines = []

        module_lines = None
        cmd_lines = None
        result_lines = None
        parsing_help = False

        for line in self.raw_julia_lines:
            if module_lines is not None and len(test_lines) == 0:
                if line.startswith(" "):
                    module_lines.append(line)
                    continue

            if cmd_lines is not None and result_lines is None:
                if not line.startswith(" "):
                    result_lines = []
                else:
                    cmd_lines.append(line)
                    continue

            if result_lines is not None:
                if line.startswith("help?>"):
                    parsing_help = True
                    continue
                elif line.startswith("julia> "):
                    prep = self.generate_julia_module_case(cmd_lines, result_lines)
                    test_lines += prep
                    parsing_help = False
                    cmd_lines = None
                    result_lines = None
                elif not parsing_help:
                    result_lines.append(line)
                    continue

            if line.startswith("julia> "):
                if "julia> module JuliaModuleTutorial ... end" in line:
                    continue
                elif "module JuliaModuleTutorial" in line:
                    module_lines = [line.removeprefix("julia> ")]
                    continue

                stripped = line.removeprefix("julia> ")
                assert cmd_lines is None
                cmd_lines = [stripped]

        if result_lines is not None:
            test_lines += self.generate_julia_module_case(cmd_lines, result_lines)

        if module_lines is None:
            self.raw_julia_lines = [default_module_fragment(f"target/debug/lib{self.name}")]
        else:
            joined = "".join(adjust_spaces(module_lines[1:], 7, 0)).replace(
                "libjulia_module_tutorial", f"lib{self.name}"
            )
            self.raw_julia_lines = [f"{module_lines[0][:-1]}\n{joined[:-1]}\n\n"]

        self.raw_julia_lines += test_lines
        return True

    def generate(self, idx):
        self.generate_name(idx)
        logger.info(f"Generating lib test-case {self.name}")

        args = ["cargo", "new", "--lib", self.name]
        subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        os.chdir(self.name)
        with open("src/lib.rs", "w") as lib_rs:
            lib_rs.writelines(self.rust_lines)

        with open("Cargo.toml", "w") as cargo_toml:
            content = cargo_toml_lib_template(self.name, JLRS_PATH)
            cargo_toml.write(content)

        if self.raw_julia_lines and self.prepare_julia_src():
            with open("ModuleTest.jl", "w+") as module_test_jl:
                module_test_jl.writelines(self.raw_julia_lines)

        os.chdir("..")
        self.generated = True


def prepare_test_dir():
    logger.info(f"Preparing test case directory")
    path = Path("./test_cases")
    if path.exists():
        logger.debug(f"Removing old test case directory")
        shutil.rmtree(path)


def extract_tests_from_file(file_name, file_path):
    logger.debug(f"Read {file_path}")
    with open(file_path) as f:
        lines = f.readlines()

    file_tests = []
    test_case = None
    parsing_test = False

    for line in lines:
        if line.startswith("<!-- DOCTEST START -->"):
            test_case = DocTest(file_name)

            logger.debug(f"Found test start")
            if parsing_test:
                logger.error(f"Previous test parsed incompletely")
                assert not parsing_test

            parsing_test = True
            continue

        if line.startswith("<!-- DOCTEST END -->"):
            logger.debug(f"Found test end")
            if not parsing_test:
                logger.error(f"Found test end while not parsing test")
                assert parsing_test

            parsing_test = False
            file_tests.append(test_case)
            continue

        if line.startswith("<!-- LIBTEST START -->"):
            test_case = LibTest(file_name)

            logger.debug(f"Found libtest start")
            if parsing_test:
                logger.error(f"Previous test parsed incompletely")
                assert not parsing_test

            parsing_test = True
            continue

        if line.startswith("<!-- LIBTEST END -->"):
            logger.debug(f"Found libtest end")
            if not parsing_test:
                logger.error(f"Found test end while not parsing test")
                assert parsing_test

            file_tests.append(test_case)
            parsing_test = False
            continue

        if line.startswith("<!-- LIBTEST_JL START -->"):
            logger.debug(f"Found libtest jl end")
            if parsing_test:
                logger.error(f"Previous test parsed incompletely")
                assert not parsing_test

            parsing_test = True
            test_case.set_parsing_julia()
            continue

        if line.startswith("<!-- LIBTEST_JL END -->"):
            logger.debug(f"Found libtest jl end")
            if not parsing_test:
                logger.error(f"Found test end while not parsing test")
                assert parsing_test

            parsing_test = False
            continue

        if parsing_test and not line.startswith("```"):
            test_case.append(line)

    if parsing_test:
        logger.error(f"Did not find test end while parsing test")
        assert not parsing_test

    return file_tests


def create_test_crate(name, cargo_toml_content):
    logger.info(f"Create test crate {name}")
    subprocess.run(
        ["cargo", "new", name], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    os.chdir(name)

    with open("Cargo.toml", "w") as cargo_toml:
        cargo_toml.write(cargo_toml_content)

    os.chdir("..")


def main():
    prepare_test_dir()
    cargo_toml = cargo_toml_bin_template(JLRS_PATH)

    docfiles = sorted(glob.glob("src/**/*.md", recursive=True))
    abs_paths = [Path(file_name).resolve() for file_name in docfiles]

    create_test_crate("test_cases", cargo_toml)

    os.chdir("test_cases")

    test_cases = []
    for file_name, abs_path in zip(docfiles, abs_paths):
        logger.info(f"Check {file_name} for tests")
        extracted_tests = extract_tests_from_file(file_name, abs_path)

        try:
            for idx, test_case in enumerate(extracted_tests):
                test_case.generate(idx)
                test_cases.append(test_case)
        except Exception as e:
            logger.error(f"Cannot generate test case {e}")
            assert False


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
