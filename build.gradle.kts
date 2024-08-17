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
    }

    jar {
        archiveFileName.set("polyglot.jar")
        destinationDirectory.set(layout.buildDirectory)
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
            addAll(getPythonConfigArgs("--includes"))
            addAll(getPythonConfigArgs("--ldflags"))
        })

        doFirst {
            println("Executing:\n${commandLine.joinToString(" ")}")
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

    /**
     * Task to copy dependency libraries and create symbolic links without version numbers.
     *
     * This task performs the following operations:
     * 1. Copies all runtime classpath dependencies to the build/libs directory.
     * 2. Creates symbolic links for each JAR file, removing version numbers from the filenames.
     */
    val copyDependencies by registering(Copy::class) {
        description = "Copies dependencies and creates symlinks without version numbers"
        group = "build"

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
