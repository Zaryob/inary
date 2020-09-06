class inary:
    class source:
        name = "ciksemel"
        homepage = "http://github.com/SulinOS/"

        class packager:
            name = "Süleyman Poyraz"
            email = "zaryob.dev@gmail.com"
        license = "GPLv2"
        isa = ["app:console"]
        partof = "bystem.base"
        summary = "ciksemel is iksemel based xml library."
        description = "Application deployment framework for desktop apps"
        archive = [("6daf8319453645dd8bae2d85e22f7a6ae08a2d1c",
                    "https://gitlab.com/sulinos/devel/ciksemel/-/archive/ciklemel-1.1/ciksemel-ciklemel-1.1.tar.gz")]
        builddependencies = ["python3-devel"]
        additionalfiles = [
            ("config", ".config"),
            ("test", ".test")
        ]
        patches = ["fix-1.patch"]
        packages = ["package", "package_devel"]

    class package:
        name = "ciksemel"
        runtimedependencies = ["python3"]
        files = [("library", "/usr/lib/sulin/ciksemel*")]
        additionalfiles = [
            ("config", "root", "0755", ".config")
        ]

    class package_devel:
        name = "ciksemel-devel"
        runtimedependencies = ["python3"]
        files = [("library", "/usr/lib/sulin/ciksemel*")]
        additionalfiles = [
            ("config", "root", "0755", ".config")
        ]

    class history:
        update = [
            ["2020-06-21", "1.1", "Python 3.8 rebuild",
                "Suleyman Poyraz", "zaryob.dev@gmail.com"],
            ["2019-09-17", "1.1", "Package is rebuilded and released up.",
                "Suleyman Poyraz", "zaryob.dev@gmail.com"],
            ["2019-09-17", "1", "Package is rebuilded and released up.",
                "Suleyman Poyraz", "zaryob.dev@gmail.com"],
            ["2019-09-17", "1", "First release",
                "Suleyman Poyraz", "zaryob.dev@gmail.com"]
        ]
