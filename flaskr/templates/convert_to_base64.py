import base64

if __name__ == '__main__':

    # Open the image file in binary mode
    with open("001.png", "rb") as image_file:
        # Read the file and encode it to base64
        encoded_string = base64.b64encode(image_file.read())

    # Write the base64 string to a file
    with open("001.txt", "w") as output_file:
        output_file.write(encoded_string.decode('utf-8'))

    print("Base64 string has been written to base64_output.txt")
