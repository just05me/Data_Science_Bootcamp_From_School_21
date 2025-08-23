import sys


def input_from_commandLine():
    val = sys.argv

    if len(val) != 4:
        raise Exception("Invalid argument")
    elif val[1] not in ["encode", "decode"]:
        raise Exception("Invalid argument")
    try:
        key = int(val[3])
    except ValueError:
        raise Exception("Invalid argument")
    
    return val[1], val[2], key
    

def encode(val: str, key: int):
    res = []
    dictionary, dictionary_upper = "abcdefghijklmnopqrstuvwxyz", "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    for char in val:

        if char in dictionary:
            ind = dictionary.index(char)
            new_ind = (ind + key) % len(dictionary)
            res.append(dictionary[new_ind])

        elif char in dictionary_upper:
            ind = dictionary_upper.index(char)
            new_ind = (ind + key) % len(dictionary_upper)
            res.append(dictionary_upper[new_ind])
        
        else:
            res.append(char)
    
    return ''.join(res)


def decode(val: str, key: int):
    return encode(val, -key)


def output(code: str):
    print(code)


def main():
    tipe, val, key = input_from_commandLine()
    supported = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")

    if any(char.isalpha() and char not in supported for char in val):
        raise Exception("The script does not support your language yet.")
    if tipe == "encode":
        cod_it = encode(val, key)
        output(cod_it)
    elif tipe == "decode":
        decode_it = decode(val, key)
        output(decode_it)


if __name__ == "__main__":
    main()