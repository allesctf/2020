#!/usr/bin/python3
def make_secure():
    original = __builtins__.__dict__.copy()
    __builtins__.__dict__.clear()
    safe_builtins = ["repr", "str", "print", "eval", "input", "any", "exec", "all", "Exception"]
    for func in safe_builtins:
        __builtins__.__dict__[func] = original[func]

def string_xor(s1,s2):
    return "".join(CHARACTER(ASCII_CODE(a) ^ ASCII_CODE(b)) for a,b in ZIP_FUNC(s1,s2))

def ALLES(flag=False):
    if flag:
        return(string_xor("p\x7f\x7frbH\x00DR\x07CRUlJ\x07DlRe\x02N", flag))
    else:
        return("No flag for you!")
print("The flag is stored super secure in the function ALLES !")
CHARACTER = chr
ZIP_FUNC = zip
ASCII_CODE = ord
denied = ["import", "upper", "lower", "open", "exit", "compile", "chr", "__import__", "object", "assert", "__builtins__", "exec", "pper", "per"]
charset = ['"', '\'', '(', ')', '+', '.', '0', '1', '2', '3', '7', '9', '[', ']', '_', 'e','v','a','l','c','s','g','t','r','p','i','n','o','d']
make_secure()
while True:
    text = input(">>> a = ").lower()
    for char in text:
     if char not in charset:
      print(char)
    if any(word in text for word in denied) or not all(char in charset for char in text):
        print("Denied")
    else:
        try:
            exec("a="+text)
        except Exception as error:
            print(error)

