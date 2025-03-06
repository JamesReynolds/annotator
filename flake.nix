{
  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
  };

  outputs = { self, flake-utils, nixpkgs }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = (import nixpkgs) {
          inherit system;
        };

      in rec {
        devShells.default = pkgs.mkShell {
          venvDir = "./venv";
          buildInputs = with pkgs; with python3Packages; [
            appimage-run
            python3
            venvShellHook
            numpy
            pandas
            openpyxl
          ];
        };
  });
}
