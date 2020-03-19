import sqlite3

def convertToBinaryData(filename):
    #Convert digital data to binary format
    with open(filename, 'rb') as file:
        blobData = file.read()
    return blobData

def insertBLOB(id, name, cost, details, category_id, sid, image_file1, image_file2, image_file3, image_file4, stock):
    try:
        conn = sqlite3.connect('C:/Users/Shreya/Documents/EcommerceWebsite/ecommerceweb/site1.db')
        cursor = conn.cursor()
        print("Connected to SQLite")
        sqlite_insert_blob_query = """ INSERT INTO product
                                  (pid, name, cost, details, category_id, sid, image_file1, image_file2, image_file3, image_file4, stock) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        if image_file1:
            img1 = convertToBinaryData(image_file1)
        else:
            img1=None
        if image_file2:
            img2 = convertToBinaryData(image_file2)
        else:
            img2=None
        if image_file3:
            img3 = convertToBinaryData(image_file3)
        else:
            img3=None
        if image_file4:
            img4 = convertToBinaryData(image_file4)
        else:
            img4=None
        # Convert data into tuple format
        data_tuple = (id, name, cost, details, category_id, sid, img1, img2, img3, img4, stock)
        cursor.execute(sqlite_insert_blob_query, data_tuple)
        conn.commit()
        print("Image and file inserted successfully as a BLOB into a table")
        cursor.close()

    except sqlite3.Error as error:
        print("Failed to insert blob data into sqlite table", error)
    finally:
        if (conn):
            conn.close()
            print("the sqlite connection is closed")



insertBLOB(44, "Ayurveda Rose & Jasmine Hair Cleanser (Shampoo), 200ml", 400, 
'A mild hair cleanser made with pure essential oils of rose and jasmine and blended with vegetable soy protein binds. Moisturises and improves the tensile strength of hair, mitigates the damage of bleaching, perming and hot combing. A 97.5% natural formula , free of SLES (sulphates), parabens and petrochemicals. Apply on wet hair, leave for 2 minutes and rinse with water.', 
3, 1, "C:/Users/Shreya/Documents/EcommerceWebsite/ecommerceweb/static/product images/ayurveda111.jpg"
, None,
 None,
  None, 35)
