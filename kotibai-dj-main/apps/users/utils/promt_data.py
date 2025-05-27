ask_question_prompt = """ Imagine you are a knowledgeable and helpful AI assistant tasked with answering user questions. Your goal is to provide clear, concise, and accurate responses that cater to the user's needs and level of understanding. Consider using real-world examples, analogies, or step-by-step explanations when appropriate. Strive for a friendly and approachable tone throughout your answers. Keep in mind that your responses should be informative, engaging, and, if necessary, provide additional resources or further guidance. Now, please generate a response to the user's question
"""

summary_prompt = '''Given the text, please follow these instructions to generate a comprehensive summary:

 1. Provide a brief overview of the main theme of the text.

 2. Identify and list any sub-themes present within the text. For each sub-theme, provide a concise summary highlighting its significance.

 3. Extract and elaborate on the key points mentioned in the text, focusing on their implications and how they contribute to the overall narrative or argument.

 4. Finally, conclude with a succinct summary that encapsulates the essence of the text, its sub-themes, and key points.

Your goal is to present a structured and detailed analysis that offers both a broad understanding of the text and insights into its specific elements.\n\n'''

article_prompt = """
Analyze the provided text and create an article strictly based on it, following these detailed instructions:

1. Title:
   - Create a concise and informative title that clearly conveys the main topic of the article.
   - The title should be formatted in bold text.

2. Date and Place:
   - Extract the appropriate date and place from the source text.
   - If the date and place are not specified in the text, leave placeholders like "Date — Place () —".
   - Include them at the beginning of the article in one paragraph, formatted as:
     *"Date — Place () —"* followed by the first paragraph of the article.
   - Leave the parentheses empty for the news agency, so the journalist can insert their own.
   - The date and place should be in regular font.


3. Introduction:
   - Write an introduction that provides a brief overview of the main topic.
   - The introduction should be written in *italic text*.
   - Do not include the word "Introduction" in the final text.

4. Main Events and Quotes:
   - Identify the main themes and create sections for each, without including section titles in the final article.
   - Each theme should have at least 3-4 quotes that reveal the essence.
   - Subheadings for each theme should be formatted in bold text.
   - When using quotes:
     - Use only quotes and names exactly as they appear in the source text.
     - Do not invent any names, quotes, or information.
     - Enclose the quote in quotation marks "“”".
     - The quote text should be in *italic text*.
     - After the quote, include a phrase like:
       - "— noted [position or name]"
       - "— said [position]"
       - "— mentioned [name]"
       - "— emphasized [position and last name]"
     - This phrase should be formatted in bold text.
     - Alternate these phrases to avoid repetition.

5. Formatting Guidelines:
   - Do not include section headers like "Introduction:", "Main Events and Quotes:", "Conclusion:" in the final article.
   - Ensure the article flows naturally without explicit section divisions.
   - Use only the information provided in the source text.
   - Do not add any additional information, names, or quotes not present in the source text.
   - Apply the specified formatting (bold, italics) where required.

6. Conclusion:
   - Summarize the main points discussed, highlighting key findings and insights.
   - Provide a future outlook and mention ongoing actions or unresolved issues.
   - Conclude with final remarks emphasizing the importance of the topic.
   - Do not include the word "Conclusion" in the final text.

7. Author and Editor:
   - Include information about who prepared and edited the article.
   - Use the template: "**Prepared by [Your Name], edited by [Editor's Name].**"

Goal:

Create a structured and well-organized article that is informative and comprehensive, following a logical flow. The article should cover various perspectives, including direct quotes from the source text, ensuring the reader fully understands the discussed issues.

Now, using the provided text, generate the article following these instructions.
"""
news_prompt = """
Analyze the provided text and create a news article strictly based on it, following these detailed instructions:

1. Title:
   - Create a concise and informative title that clearly conveys the main topic of the article.
   - The title should be formatted in bold text.

2. Date and Place:
   - Extract the appropriate date and place from the source text.
   - If the date and place are not specified in the text, leave placeholders like "Date — Place () —".
   - Include them at the beginning of the article in one paragraph, formatted as:
     *"Date — Place () —"* followed by the first paragraph of the article.
   - Leave the parentheses empty for the news agency, so the journalist can insert their own.
   - The date and place should be in regular font.

3. Introduction:
   - Write an introduction that provides a brief overview of the main news.
   - The introduction should be written in *italic text*.
   - Do not include the word "Introduction" in the final text.

4. Body of the News Article:
   - Organize the article using the inverted pyramid style, starting with the most important information and following with supporting details.
   - Identify the key facts and present them clearly and concisely.
   - Use paragraphs to separate different points or aspects of the news.
   - Include direct quotes from the source text to enhance credibility and provide authoritative perspectives.
     - Use only quotes and information exactly as they appear in the source text.
     - Do not invent any names, quotes, or information.
     - Enclose the quote in quotation marks "“”".
     - The quote text should be in *italic text*.
     - After the quote, include a phrase like:
       - "— noted [position or name]"
       - "— said [position]"
       - "— mentioned [name]"
       - "— emphasized [position and last name]"
     - This phrase should be formatted in bold text.
     - Alternate these phrases to avoid repetition.
   - Ensure that the article flows logically and that all information is connected and relevant.

5. Formatting Guidelines:
   - Do not include section headers like "Introduction:", "Body of the News Article:", "Conclusion:" in the final article.
   - Ensure the article flows naturally without explicit section divisions.
   - Use only the information provided in the source text.
   - Do not add any additional information, names, or content not present in the source text.
   - Apply the specified formatting (bold, italics) where required.

6. Conclusion:
   - Provide any concluding remarks or lesser details that are still relevant to the news.
   - Do not include the word "Conclusion" in the final text.

7. Author and Editor:
   - Include information about who prepared and edited the article.
   - Use the template: "**Prepared by [Your Name], edited by [Editor's Name].**"

Goal:

Create a structured and well-organized news article that is informative and comprehensive, following a logical flow. The article should present the most important information first, followed by supporting details, ensuring the reader fully understands the news. Strictly adhere to the source material, avoiding any hallucinations or invented content. Internally verify all quotes and information against the source text before finalizing the article. Do not include the verification process in the final output.

Now, using the provided text, generate the article following these instructions.
"""
reportage_prompt = """
Analyze the provided text and create an article strictly based on it, following these detailed instructions:

1. Title:
   - Create a concise and informative title that clearly conveys the main topic of the article.
   - The title should be formatted in bold text.

2. Date and Place:
   - Extract the appropriate date and place from the source text.
   - If the date and place are not specified in the text, leave placeholders like "Date — Place () —".
   - Include them at the beginning of the article in one paragraph, formatted as:
     *"Date — Place () —"* followed by the first paragraph of the article.
   - Leave the parentheses empty for the news agency, so the journalist can insert their own.
   - The date and place should be in regular font.

3. Introduction:
   - Write an introduction that provides a brief overview of the main topic.
   - The introduction should be written in *italic text*.
   - Do not include the word "Introduction" in the final text.

4. Report Body with Subthemes:
   - Analyze the source text to identify key subthemes.
   - For each subtheme:
     - Write the subtheme title, formatted in bold text.
     - Under the subtheme title, provide detailed paragraphs that describe the events, observations, and information related to the subtheme, strictly based on the source material.
     - Include at least four direct quotes or statements from the source text that enhance the narrative.
       - Use only quotes and information exactly as they appear in the source text.
       - Do not invent any names, quotes, or information.
       - Enclose the quote in quotation marks "“”".
       - The quote text should be in *italic text*.
       - After the quote, include a phrase like:
         - "— noted [position or name]"
         - "— said [position]"
         - "— mentioned [name]"
         - "— emphasized [position and last name]"
       - This phrase should be formatted in bold text.
       - Alternate these phrases to avoid repetition.
     - Ensure that the narrative flows smoothly, combining descriptive passages with quotes.
   - Do not invent any additional subthemes, quotes, names, or information.
   - Internally, carefully verify that all content and quotes exactly match the source text. Double-check for any discrepancies or invented content before finalizing the article. Do not include this verification process in the final article.

5. Formatting Guidelines:
   - Do not include section headers like "Introduction:", "Report Body with Subthemes:", "Conclusion:" in the final article.
   - Ensure the article flows naturally without explicit section divisions.
   - Use only the information provided in the source text.
   - Do not add any additional information, names, or content not present in the source text.
   - Apply the specified formatting (bold, italics) where required.

6. Conclusion:
   - Summarize the main points discussed, highlighting key findings and insights.
   - Provide a future outlook and mention ongoing actions or unresolved issues.
   - Conclude with final remarks emphasizing the importance of the topic.
   - Do not include the word "Conclusion" in the final text.

7. Author and Editor:
   - Include information about who prepared and edited the article.
   - Use the template: "**Prepared by [Your Name], edited by [Editor's Name].**"

Goal:

Create a structured and well-organized article in report format that is informative and comprehensive, following a logical flow. The article should present the subthemes clearly, with detailed paragraphs and direct quotes that fully cover each topic, ensuring the reader fully understands the discussed issues. Strictly adhere to the source material, avoiding any hallucinations or invented content. Internally verify all quotes and information against the source text before finalizing the article. Do not include the verification process in the final output.

Now, using the provided text, generate the article following these instructions.
"""
interview_prompt = """
Analyze the provided text and create an article strictly based on it, following these detailed instructions:

1. Title:
   - Create a concise and informative title that clearly conveys the main topic of the article.
   - The title should be formatted in bold text.

2. Date and Place:
   - Extract the appropriate date and place from the source text.
   - If the date and place are not specified in the text, leave placeholders like "Date — Place () —".
   - Include them at the beginning of the article in one paragraph, formatted as:
     *"Date — Place () —"* followed by the first paragraph of the article.
   - Leave the parentheses empty for the news agency, so the journalist can insert their own.
   - The date and place should be in regular font.

3. Introduction:
   - Write an introduction that provides a brief overview of the main topic.
   - The introduction should be written in *italic text*.
   - Do not include the word "Introduction" in the final text.

4. Interview Format with Subthemes:
   - Analyze the source text to identify key subthemes.
   - For each subtheme:
     - Write the subtheme title, formatted in bold text.
     - Under the subtheme title, include at least four question and answer pairs that fully cover the topic, strictly based on the source material.
     - Format each question and answer pair as follows:
       - Question: The question text.
       - Answer: The answer text.
     - The words "Question:" and "Answer:" should be formatted in bold text.
     - The question and answer texts should be in regular font.
     - Ensure that each question and answer pair is clearly separated for readability.
   - Do not invent any additional subthemes, questions, answers, names, or information.
   - Internally, carefully verify that all questions, answers, and quotes exactly match the source text. Double-check for any discrepancies or invented content before finalizing the article. Do not include this verification process in the final article.

5. Formatting Guidelines:
   - Do not include section headers like "Introduction:", "Interview Format with Subthemes:", "Conclusion:" in the final article.
   - Ensure the article flows naturally without explicit section divisions.
   - Use only the information provided in the source text.
   - Do not add any additional information, names, or content not present in the source text.
   - Apply the specified formatting (bold, italics) where required.

6. Conclusion:
   - Summarize the main points discussed, highlighting key findings and insights.
   - Provide a future outlook and mention ongoing actions or unresolved issues.
   - Conclude with final remarks emphasizing the importance of the topic.
   - Do not include the word "Conclusion" in the final text.

7. Author and Editor:
   - Include information about who prepared and edited the article.
   - Use the template: "**Prepared by [Your Name], edited by [Editor's Name].**"

Goal:

Create a structured and well-organized article in interview format that is informative and comprehensive, following a logical flow. The article should present the subthemes clearly, with questions and answers that fully cover each topic, ensuring the reader fully understands the discussed issues. Strictly adhere to the source material, avoiding any hallucinations or invented content. Internally verify all quotes and information against the source text before finalizing the article. Do not include the verification process in the final output.

Now, using the provided text, generate the article following these instructions.
"""

medic_prompt = """
    You should create a template for a doctor based on the text given below,
    its conversation between doctor and patient. you should first, 
    create information about patient, 
    and in the end create suggestions for doctor, 
    like what illnes it could be, or what to ask more:
    
"""

uz_ru_prompt = """Translate the given text from Uzbek to Russian as an experienced philologist with 50 years of experience. Additionally, make corrections and edits based on meaning and context as an experienced journalist, proofreader, and editor without changing the essence of the text. The translation should not be a simple mechanical one; it needs to reflect a deep understanding of both languages and cultures."""

uz_en_prompt = """Translate the given text from Uzbek to English as an experienced philologist with 50 years of experience. Additionally, make corrections and edits based on meaning and context as an experienced journalist, proofreader, and editor without changing the essence of the text. The translation should not be a simple mechanical one; it needs to reflect a deep understanding of both languages and cultures."""

ru_uz_prompt = """Translate the given text from Russian to Latin Uzbek as an experienced philologist with 50 years of experience. Additionally, make corrections and edits based on meaning and context as an experienced journalist, proofreader, and editor without changing the essence of the text. The translation should not be a simple mechanical one; it needs to reflect a deep understanding of both languages and cultures."""

ru_en_prompt = """Translate the given text from Russian to English as an experienced philologist with 50 years of experience. Additionally, make corrections and edits based on meaning and context as an experienced journalist, proofreader, and editor without changing the essence of the text. The translation should not be a simple mechanical one; it needs to reflect a deep understanding of both languages and cultures."""

en_uz_prompt = """Translate the given text from English to Latin Uzbek  as an experienced philologist with 50 years of experience. Additionally, make corrections and edits based on meaning and context as an experienced journalist, proofreader, and editor without changing the essence of the text. The translation should not be a simple mechanical one; it needs to reflect a deep understanding of both languages and cultures."""

en_ru_prompt = """Translate the given text from English to Russian as an experienced philologist with 50 years of experience. Additionally, make corrections and edits based on meaning and context as an experienced journalist, proofreader, and editor without changing the essence of the text. The translation should not be a simple mechanical one; it needs to reflect a deep understanding of both languages and cultures."""

auto_en_prompt = """The given text can be in Uzbek, Russian and English. Translate this text into English as an experienced philologist with 50 years of experience. Also, as an experienced journalist, proofreader and editor, make corrections and edits based on meaning and context without changing the essence of the text. Translation should not be merely mechanical; it should reflect a deep understanding of both languages and cultures."""

auto_uz_prompt = """The given text can be in Uzbek, Russian and English. Translate this text into Latin Uzbek as an experienced philologist with 50 years of experience. Also, as an experienced journalist, proofreader and editor, make corrections and edits based on meaning and context without changing the essence of the text. Translation should not be merely mechanical; it should reflect a deep understanding of both languages and cultures."""

auto_ru_prompt = """The given text can be in Uzbek, Russian and English. Translate this text into Russian as an experienced philologist with 50 years of experience. Also, as an experienced journalist, proofreader and editor, make corrections and edits based on meaning and context without changing the essence of the text. Translation should not be merely mechanical; it should reflect a deep understanding of both languages and cultures."""

transcript_edit_prompt_uz = """Please process the following text written in Uzbek - Latin script. Correct only grammar (spelling), punctuation, and paragraphs, and if the Uzbek text is in Cyrillic, convert it to Latin. Remove unnecessary prefixes such as "(Music)" from the beginning of lines. Check and fix the spelling of names, locations, and well-known terms only if they are incorrect. Do not shorten, rephrase, rewrite, replace words, or change sentence structure. The wording and order of the text must remain exactly as in the original.\n\n"""
transcript_edit_prompt_ru = """Please process the following text written in Russian. Correct only grammar (spelling), punctuation, and paragraphing. Remove unnecessary prefixes such as '(Muzik)' from the beginning of lines. Check and fix the spelling of names, locations, and well-known terms only if they are incorrect. Do not shorten, rephrase, rewrite, replace words, or change sentence structure. The wording and order of the text must remain exactly as in the original.\n\n"""
transcript_edit_prompt_en = """Please process the following text written in English. Correct only grammar (spelling), punctuation, and paragraphing. Remove unnecessary prefixes such as '(Muzik)' from the beginning of lines. Check and fix the spelling of names, locations, and well-known terms only if they are incorrect. Do not shorten, rephrase, rewrite, replace words, or change sentence structure. The wording and order of the text must remain exactly as in the original.\n\n"""
