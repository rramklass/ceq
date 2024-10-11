# ceq
Certification Exam Questions.

This GenAI solution leverages Amazon Bedrock LLMs and a Knowledge Base as well as a streamlit UI to generate Certification Exam MCQ style questions for self-study or test publishers. The LLM content is augmented using Exam specific artifacts, including certification exam books, exam guides, sample questions etc. 

## Architecture
![image](https://github.com/user-attachments/assets/bce6a247-a0a7-4db4-859d-9412f31c9da7)

## Prerequisites

### S3 Bucket

Artifacts needed to seed the knowledge base (KB) must be loaded into an S3 bucket. These files tend to be relatively small, and it is more cost efficient to use one KB for all the content. 

As you load your artifacts into your S3 bucket, it works well to structure the folders by vendor and exam code. In the example below, three folders for vendors (in red) were created in the S3 bucket viz. aws, azure, and oracle. But this works for any vendor or exam. The exam code (in green) is another level, for example SAPC02. Finally, exam specific artifacts (in yellow) are uploaded. 

![image](https://github.com/user-attachments/assets/966239ef-2854-43b4-a19c-6408497c8dae)

### Bedrock Knowledge Base 

Create a KB. An easy way is to use the AWS console to create and access a knowledge base created using the S3 bucket described earlier as a data source and to sync the KB each time you add/remove content from the KB. 
Several prompts were developed to extract the exam questions in the desired format, using Bedrock Prompt Management. 

![image](https://github.com/user-attachments/assets/6185b81d-5898-4882-9cac-7bfe6c5adb2c)

## Application

The application was created using VS code in Python using streamlit for the UI. 
The video below shows how the application works to analyze the exam domains to be measured. This is then used to generate domain specific exam questions. Input dialog boxes also show you can customize the output by specifying the number of questions to generate, number to MCQ options and length of the answer. 

https://github.com/user-attachments/assets/9b42360c-306a-4c99-9a56-085f59f5d469

