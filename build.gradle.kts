plugins {
    kotlin("jvm") version "1.9.20"
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

    build {
        dependsOn(compileCpp, compilePython)
    }
}

kotlin {
    jvmToolchain(11)
}

layout.buildDirectory.set(file("build-out"))

fun getPythonConfigArgs(config: String): List<String> =
    "python3-config $config".runCommand()
        .trim()
        .split(" ")
        .filter(String::isNotEmpty)

fun String.runCommand(): String =
    ProcessBuilder(this.split(" "))
        .redirectErrorStream(true)
        .start()
        .inputStream
        .bufferedReader()
        .readText()
