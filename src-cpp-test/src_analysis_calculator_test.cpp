#include "src_analysis_calculator.h"

#include <glog/logging.h>
#include <gtest/gtest.h>


/** Test fixture class for SrcAnalysisCalculator */
class SrcAnalysisCalculatorTest : public ::testing::Test {
protected:
    void SetUp() override {}
    void TearDown() override {}
};


TEST_F(SrcAnalysisCalculatorTest, AnalyzeCpp) {
    const std::string kFilePathCpp = "test_cpp.cpp";
    const std::string kFileContentCpp = R"(\
#include <iostream>

/**
 * This is a
 * multiline comment
 */
int main() {
    // This is a single-line comment
    LOG(INFO) << "Hello, World!";
    return 0;
}

// Forward declaration
class ForwardDeclaredClass;
)";

    SrcAnalysisCalculator calculator(kFilePathCpp);
    FileStats stats = calculator.analyze(kFileContentCpp);

    EXPECT_EQ(stats.total_lines, 15);
    EXPECT_EQ(stats.code_lines, 3);
    EXPECT_EQ(stats.comment_lines, 6);
    EXPECT_EQ(stats.import_lines, 1);
    EXPECT_EQ(stats.logging_lines, 1);
    EXPECT_EQ(stats.total_classes, 0);
    EXPECT_EQ(stats.trivial_lines, 1);
    EXPECT_EQ(stats.empty_lines, 2);
    EXPECT_EQ(stats.multistring_lines, 0);
}

TEST_F(SrcAnalysisCalculatorTest, AnalyzePython) {
    const std::string kFilePathPy = "test_py.py";
    const std::string kFileContentPy = R"(\
from loguru import logger

# This is a single-line comment
def main():
    '''This is a
       multiline string in Python'''
    logger.info('Hello, World!')

if __name__ == '__main__':
    main()
)";

    SrcAnalysisCalculator calculator(kFilePathPy);
    FileStats stats = calculator.analyze(kFileContentPy);

    EXPECT_EQ(stats.total_lines, 11);
    EXPECT_EQ(stats.code_lines, 4);
    EXPECT_EQ(stats.comment_lines, 1);
    EXPECT_EQ(stats.import_lines, 1);
    EXPECT_EQ(stats.logging_lines, 1);
    EXPECT_EQ(stats.total_classes, 0);
    EXPECT_EQ(stats.trivial_lines, 0);
    EXPECT_EQ(stats.empty_lines, 2);
    EXPECT_EQ(stats.multistring_lines, 3);
}

TEST_F(SrcAnalysisCalculatorTest, AnalyzeKotlin) {
    const std::string kFilePathKt = "test_kt.kt";
    const std::string kFileContentKt = R"(\
package com.example

import org.slf4j.Logger

private val logger: Logger = LoggerFactory.getLogger("HelloWorld")

/**
 * This is a multiline comment in Kotlin
 */
fun main() {
    // This is a single-line comment
    println("Hello, World!")  // Print a message
}

data class Example(val name: String)
)";

    SrcAnalysisCalculator calculator(kFilePathKt);
    FileStats stats = calculator.analyze(kFileContentKt);

    EXPECT_EQ(stats.total_lines, 16);
    EXPECT_EQ(stats.code_lines, 5);
    EXPECT_EQ(stats.comment_lines, 4);
    EXPECT_EQ(stats.import_lines, 1);
    EXPECT_EQ(stats.logging_lines, 0);
    EXPECT_EQ(stats.total_classes, 1);
    EXPECT_EQ(stats.trivial_lines, 1);
    EXPECT_EQ(stats.empty_lines, 4);
    EXPECT_EQ(stats.multistring_lines, 0);
}


int main(int argc, char** argv) {
    google::InitGoogleLogging(argv[0]);
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
