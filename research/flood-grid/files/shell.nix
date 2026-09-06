{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShell {
  packages = [ pkgs.uv pkgs.python313 ];
  LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [ pkgs.expat pkgs.stdenv.cc.cc.lib ];
}
