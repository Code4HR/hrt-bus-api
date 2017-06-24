from selenium import webdriver

def before_all(context):
    context.browser = webdriver.PhantomJS()
