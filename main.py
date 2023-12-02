from traceback import print_exc

if __name__ == "__main__":
    try:
        pass
    except Exception as e:
        print('Error occured:')
        print_exc()