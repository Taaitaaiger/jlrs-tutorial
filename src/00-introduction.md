# Introduction

jlrs is a crate for Rust-Julia interop. It can be used to embed Julia in Rust applications, and to create dynamic libraries that expose functionality written in Rust to Julia. This tutorial will get you up to speed to effectively use jlrs.

After installing all dependencies, we'll start embedding Julia in Rust applications. Important topics are introduced incrementally, later chapters will build on information found in earlier ones. When we've gotten familiar with jlrs, two additional runtimes are introduced. The final major topic is exposing Rust code to Julia, first without using jlrs and then with.

If you're not interested in embedding Julia, you can skip the additional runtime chapters and read the chapters about dynamic libraries instead. If you're only interested in exposing Rust code to Julia without using jlrs, reading chapters 5 and 11 should be sufficient.
