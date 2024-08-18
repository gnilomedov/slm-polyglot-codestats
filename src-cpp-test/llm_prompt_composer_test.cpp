#include "llm_prompt_composer_impl.h"

#include <algorithm>

#include <glog/logging.h>
#include <gtest/gtest.h>


/** Test fixture class for LlmPromptComposer */
class LlmPromptComposerTest : public ::testing::Test {
protected:
    LlmPromptComposer composer;

    void SetUp() override {}
    void TearDown() override {}
};


TEST_F(LlmPromptComposerTest, ComposePromptLinesTest) {
    // Arrange
    const char* kTestFilePathCpp = "test.cpp";
    const char* kTestFileContentCpp = R"(\
#include <iostream>
int main() {
    std::cout << "Hello, World!";
    return 0;
}
)";

    const char* kTestFilePathPy = "test.py";
    const char* kTestFileContentPy = R"(\
import sys
print('Hello, World!')
sys.exit(0)
)";

    const char* kExpectedPreamble = "Assist me in improving programming code.";
    const char* kExpectedInstructionStart =
        "Start with the most critical / important improvements pick 1 to 3 items.";

    std::vector<std::pair<std::string, std::string>> path_and_contents = {
        {kTestFilePathCpp, kTestFileContentCpp},
        {kTestFilePathPy, kTestFileContentPy},
    };

    // Act
    std::vector<std::string> prompt_txt = composer.composePromptLines(path_and_contents);

    // Assert
    ASSERT_FALSE(prompt_txt.empty());
    EXPECT_EQ(prompt_txt.front(), kExpectedPreamble);

    auto it = std::find(prompt_txt.begin(), prompt_txt.end(), "=== FILE PATH ===");
    ASSERT_NE(it, prompt_txt.end()) << "File path marker not found for C++ file";
    EXPECT_EQ(*(it + 1), kTestFilePathCpp);

    it = std::find(it, prompt_txt.end(), "=== FILE CONTENT ===");
    ASSERT_NE(it, prompt_txt.end()) << "File content marker not found for C++ file";
    EXPECT_EQ(*(it + 1), kTestFileContentCpp);

    it = std::find(it, prompt_txt.end(), "=== FILE PATH ===");
    ASSERT_NE(it, prompt_txt.end()) << "File path marker not found for Python file";
    EXPECT_EQ(*(it + 1), kTestFilePathPy);

    it = std::find(it, prompt_txt.end(), "=== FILE CONTENT ===");
    ASSERT_NE(it, prompt_txt.end()) << "File content marker not found for Python file";
    EXPECT_EQ(*(it + 1), kTestFileContentPy);

    it = std::find(prompt_txt.begin(), prompt_txt.end(), kExpectedInstructionStart);
    ASSERT_NE(it, prompt_txt.end()) << "Expected instruction not found";
}


int main(int argc, char** argv) {
    google::InitGoogleLogging(argv[0]);
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
