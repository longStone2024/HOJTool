# HOJTool

A small utility tool developed using HOJ's API at its core.

Why create it: Asking the author seems to provide no help whatsoever.

## Introduction to Implemented Functions
In fact, a part of it is AI assisted production, but it cannot be denied that AI's contribution can only account for a part.
1. * * Code crawling/retesting * *: allows crawling of code for a given number, while also revealing the remote evaluation account password (based on unauthenticated retesting implementation).
1. * * Custom submission * *: Submit code using your good friend's name or a prohibited language! (Of course, remote evaluation is required, and if the language is not supported, a 'System Error' will occur.)
2. * * Discussion crawling * *: directly crawl the discussion Markdown.
4. * * Custom post discussion * * In fact, you can customize your likes, comments, views, titles, etc
5. * * Discuss liking/de liking * *: Allow unlimited times to change likes for the discussion! (Like API unverified, but author says he wrote it)
6. * * Discussion and Reporting * *: Allow custom tags and content, and you can also choose the reporter yourself. Anyway, it's not your fault!
7. Quick refresh CFSession: Only applicable to some HOJ branches.

## Quick Start
Available in both CLI and GUI versions, with GUI already compiled!

To run the GUI version, you need to install the following libraries:  

```cmd
pip install requests ttkbootstrap pyperclip pywinstyles tkinterweb
```  

For the CLI version, only `requests` is required:  
```cmd
pip install requests
```  

This ensures compatibility with both graphical and command-line interfaces. The `requests` library is essential for HTTP operations, while additional packages like `ttkbootstrap`, `pyperclip`, and `pywinstyles` enhance GUI functionality.  

Note: Always verify Python and pip are properly installed before proceeding.
