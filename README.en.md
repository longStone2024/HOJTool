# HOJTool

A small utility tool developed using HOJ's API at its core.

Why create it: Asking the author seems to provide no help whatsoever.

## Implemented Features
Actually, some parts were AI-assisted, but it's undeniable that AI's contribution only accounts for a portion.
1. **Code Crawling/Rejudging**: Allows crawling code for given IDs while exposing remote judging account credentials (implemented through unauthorized rejudging).
2. **Custom Submission**: Submit code using your friend's name or in prohibited languages! (Requires remote judging enabled, will show `System Error` for unsupported languages, like `gene-2012`)
3. **Discussion Crawling**: Directly crawl discussion Markdown content.
4. **Discussion Like/Unlike**: Allows unlimited like status changes for discussions! (Like API lacks authentication, though author claims it's implemented)
5. **Discussion Reporting**: Allows custom tags and content, even choosing who appears as the reporter - definitely not you!
6. **Quick CFSession Refresh**: Only works for certain HOJ forks.

## Quick Start
Available in both CLI and GUI versions, with GUI already compiled!

To run the GUI version, you need to install the following libraries:  

```cmd
pip install requests ttkbootstrap pyperclip pywinstyles
```  

For the CLI version, only `requests` is required:  
```cmd
pip install requests
```  

This ensures compatibility with both graphical and command-line interfaces. The `requests` library is essential for HTTP operations, while additional packages like `ttkbootstrap`, `pyperclip`, and `pywinstyles` enhance GUI functionality.  

Note: Always verify Python and pip are properly installed before proceeding.
