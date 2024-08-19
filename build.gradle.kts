import java.nio.file.Files

plugins {
    kotlin("jvm") version "1.9.20"
    kotlin("plugin.serialization") version "1.9.20"
    `java-library`
    // Using the cpp-library plugin alongside the java-library plugin is not feasible without
    // significant custom configuration, which might introduce more complexity than it solves.
}

repositories {
    mavenCentral()
}

val mockKVersion by extra("1.13.7")

dependencies {
    implementation("ch.qos.logback:logback-classic:1.4.6")
    implementation("org.slf4j:slf4j-api:2.0.0")
    implementation("org.slf4j:slf4j-simple:2.0.0")

    implementation("com.squareup.okhttp3:okhttp:4.10.0")
    implementation("org.json:json:20230227")

    testImplementation(kotlin("test"))
    testImplementation("io.mockk:mockk:$mockKVersion")
}

sourceSets {
    main {
        kotlin.srcDir("src-kt")
    }
    test {
        kotlin.srcDir("src-kt-test")
    }
}

tasks {
    test {
        useJUnitPlatform()
        testLogging {
            events("passed", "skipped", "failed")
            showStandardStreams = true
            exceptionFormat = org.gradle.api.tasks.testing.logging.TestExceptionFormat.FULL
        }
        // Print a summary of test results.
        doLast {
            // Define the test results directory and list XML result files
            val testResultsDir = layout.buildDirectory.dir("test-results/test").get().asFile
            val testResultsFiles = testResultsDir.listFiles {
                file -> file.isFile && file.name.endsWith(".xml") } ?: emptyArray()
            val totalTests = testResultsFiles.sumOf {
                file -> file.readLines().count { it.contains("<testcase") } }
            val failedTests = testResultsFiles.sumOf {
                file -> file.readLines().count { it.contains("<failure") } }
            val skippedTests = testResultsFiles.sumOf {
                file -> file.readLines().count { it.contains("<skipped") } }
            println("""
                |
                |Test Summary:
                |===================================
                |Total tests: $totalTests
                |Failed tests: $failedTests
                |Skipped tests: $skippedTests
                |===================================
                """.trimMargin())
        }
    }

    jar {
        archiveFileName.set("polyglot.jar")
        destinationDirectory.set(layout.buildDirectory)
    }

    /**
     * Task to copy dependency libraries and create symbolic links without version numbers.
     *
     * This task performs the following operations:
     * 1. Copies all runtime classpath dependencies to the build/libs directory.
     * 2. Creates symbolic links for each JAR file, removing version numbers from the filenames.
     */
    val copyDependencies by registering(Copy::class) {
        group = "build"
        description = "Copies dependencies and creates symlinks without version numbers"

        val prefixes = listOf(
            "kotlin-stdlib",
            "slf4j-api",
            "slf4j-simple",
            "okhttp",
            "okio-jvm",
            "json"
        )
        from(configurations.runtimeClasspath) {
            include { fileTreeElement ->
                prefixes.any { prefix ->
                    fileTreeElement.file.name.startsWith(prefix)
                }
            }
        }
        into(layout.buildDirectory.dir("libs"))

        doLast {
            createSymlinksWithoutVersions()
        }
    }


    val compileAndRunCppTests by registering {
        group = "verification"
        description = "Compile and run all C++ tests"

        doLast {
            val testDir = file("src-cpp-test")
            val testFiles = testDir.walk().filter { it.name.endsWith("_test.cpp") }.toList()
            val buildDir = layout.buildDirectory.dir("bin-cpp-test").get().asFile
            buildDir.mkdirs()
            val mainSources = fileTree("src-cpp") { include("**/*.cpp") }.files.map {
                it.absolutePath }

            testFiles.forEach { testFile ->
                val testName = testFile.nameWithoutExtension
                val outputFile = buildDir.resolve(testName)
                val compileCommand = buildList {
                    add("g++")
                    addAll(listOf("-std=c++17", "-O2", "-Wall"))
                    addAll(listOf("-o", outputFile.absolutePath))
                    addAll(mainSources)
                    add(testFile.absolutePath)
                    addAll(listOf("-I", "src-cpp", "-I", "src-cpp-test"))
                    addAll(listOf("-L/usr/local/lib", "-lglog"))
                    addAll(listOf("-lgtest", "-lgtest_main", "-pthread"))
                }

                println("Compiling test: $testName\n${compileCommand.joinToString(" ")}")
                exec {
                    commandLine(compileCommand)
                    standardOutput = System.out
                    errorOutput = System.err
                }

                println("Running test: $testName")
                exec {
                    commandLine(outputFile.absolutePath)
                    environment("GTEST_COLOR", "1")
                    standardOutput = System.out
                    errorOutput = System.err
                }
            }
        }
    }

    val compileCpp by registering(Exec::class) {
        group = "build"
        description = "Compile C++ into .so"

        val cppFiles = fileTree("src-cpp") { include("**/*.cpp") }.files
        val outputFile = layout.buildDirectory.file("polyglot.so").get().asFile

        commandLine(buildList {
            add("g++")
            addAll(listOf("-std=c++17", "-O2", "-Wall", "-fPIC", "-shared"))
            addAll(listOf("-o", outputFile.absolutePath))
            addAll(cppFiles.map { it.absolutePath })
            addAll(listOf("-L/usr/local/lib", "-lglog"))
            addAll(getPythonConfigArgs("--includes"))
            addAll(getPythonConfigArgs("--ldflags"))
        })

        dependsOn(compileAndRunCppTests)

        doFirst {
            println("Executing:\n${commandLine.joinToString(" ")}")
        }

        standardOutput = System.out
        errorOutput = System.err
    }


    val runPythonTests by registering(Exec::class) {
        group = "verification"
        description = "Run all pytest tests recursively in src-py-test"

        val srcPyTestDir = file("src-py-test")
        val srcPyDir = file("src-py")

        environment("PYTHONPATH", srcPyDir.absolutePath)

        commandLine(buildList {
            add("pytest")
            addAll(listOf("--color=yes", "-v"))
            addAll(listOf("--maxfail=1", "--disable-warnings"))
            add(srcPyTestDir.absolutePath)
        })

        dependsOn(copyDependencies)

        doFirst {
            println("Executing pytest in directory: ${srcPyTestDir.absolutePath}")
            println("Command:\nPYTHONPATH=${srcPyDir.absolutePath} \\\n" +
                    "${commandLine.joinToString(" ")}")
        }

        standardOutput = System.out
        errorOutput = System.err
    }

    val compilePython by registering(Exec::class) {
        group = "build"
        description = "Compile Python into bytecode"

        val srcDir = file("src-py")
        val outputDir = layout.buildDirectory.dir("polyglot_py_bytecode").get().asFile

        doFirst {
            outputDir.mkdirs()
        }

        commandLine(buildList {
            addAll(listOf("python3", "-m", "compileall", "-f"))
            addAll(listOf("-b", srcDir.absolutePath))
            addAll(listOf("-d", outputDir.absolutePath))
        })

        dependsOn(runPythonTests)

        doFirst {
            println("Executing:\n${commandLine.joinToString(" ")}")
        }

        doLast {
            fileTree(srcDir) { include("**/*.pyc") }.forEach { pycFile ->
                val destFile = file("$outputDir/${pycFile.relativeTo(srcDir)}")
                destFile.parentFile.mkdirs()
                pycFile.renameTo(destFile)
            }
        }

        standardOutput = System.out
        errorOutput = System.err
    }


    build {
        dependsOn(compileCpp, compilePython, copyDependencies)
    }
}

kotlin {
    jvmToolchain(11)
}

layout.buildDirectory.set(file("build-out"))

/** Retrieves Python configuration arguments for the given configuration flag. */
fun getPythonConfigArgs(config: String): List<String> =
    "python3-config $config".runCommand()
        .trim()
        .split(" ")
        .filter(String::isNotEmpty)

/**
 * Executes the string as a shell command and returns the output.
 *
 * @return The output of the command as a [String].
 */
fun String.runCommand(): String =
    ProcessBuilder(this.split(" "))
        .redirectErrorStream(true)
        .start()
        .inputStream
        .bufferedReader()
        .readText()

/** Creates symbolic links for JAR files without version numbers in their names. */
fun createSymlinksWithoutVersions() {
    val libsDir = layout.buildDirectory.dir("libs").get().asFile
    val versionPattern = Regex("-\\d+(\\.\\d+)*(-\\w+)?\\.jar$")

    libsDir.listFiles()?.filter { it.isFile && it.name.endsWith(".jar") }?.forEach { file ->
        val baseName = file.name.replace(versionPattern, ".jar")
        if (baseName != file.name) {
            val symlink = File(libsDir, baseName)
            symlink.delete() // Remove existing symlink if any
            Files.createSymbolicLink(symlink.toPath(), file.toPath())
        }
    }
}
