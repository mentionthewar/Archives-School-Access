# Transforming output from data accessioner into a form importable into Discovery via MYC

import re
import codecs
import untangle
import os

count = 0

output_file = open("new_collection.txt", "a") # a for append, w for write
path = '/Users/Jo/Desktop/Digital Preservation/Archives School/Accessioner to MYC/metadata/'

collection_creator = input("Who was the original creator of this collection?: ")
collection_url = input("At what URL is this collection available to download?: ")

print("Thinking...")

output_file.write("Level\t" + "Title\t" + "Creator\t" + "Description\t" + "Reference\t" + "Start Date\t" + "End Date\t" + "Extent\t" + "Physical description\t"
                  "Related units of description (URL)\t" + "Note (fixity)\n")

# level uses folder followed by file
# title is file.name
# creator is user defined for fonds level only
# description we could leave blank but let's use the ingest note
# reference is the accession number with augmentation for each file/folder
# start date and end date are the last modified date twice. Take the first 10 characters and lose the hyphens
# Extent is 'Digital file' followed by PREMIS:Size (gives a number in bytes / by 1024 to produce a value in kilobytes)
# physical description is the file format in premis:formatName
# note is the checksum - the file's MD5 value


for filename in os.listdir(path):
    filename_p = path + filename

    accession_file = codecs.open(filename_p, 'r', encoding='utf-8', errors='replace')
    xml = untangle.parse(accession_file)

    # Produce fonds level information

    level = 'fonds'
    collection_title = xml.collection['name']
    collection_description = xml.collection.accession.ingest_note.cdata
    collection_reference = xml.collection.accession['number']

    collection_start_date = xml.collection.accession.folder['last_modified']
    collection_start_date = collection_start_date[0:10] 
    collection_start_date = collection_start_date.replace('-','')
    collection_end_date = collection_start_date

    collection_extent = str(len(xml.collection.accession.folder)) + " digital files"

    output_file.write(level+ "\t" + collection_title + "\t" + collection_creator + "\t" + collection_description + "\t" + collection_reference + "\t" + collection_start_date + "\t"
                      + collection_end_date + "\t" + collection_extent + "\t" + "\t" + collection_url + "\n")

    # Produce piece/folder level information

    level = 'file'
    piece_title = xml.collection.accession.folder['name']
    piece_creator = collection_creator
    piece_reference = collection_reference + "/1"
    piece_start_date = collection_start_date
    piece_end_date = piece_start_date
    piece_extent = collection_extent

    output_file.write(level+ "\t" + piece_title + "\t" + piece_creator + "\t" + "\t" + piece_reference + "\t" + piece_start_date + "\t"
                      + piece_end_date + "\t" + piece_extent + "\n")

    # Produce item level information
    extent = len(xml.collection.accession.folder)
    
    while count < extent:
        level = 'item'
        item_title = xml.collection.accession.folder.file[count]['name']
        item_reference = piece_reference + "/" + str(count + 1)
        
        item_start_date = xml.collection.accession.folder.file[count]['last_modified']
        item_start_date = collection_start_date[0:10] 
        item_start_date = collection_start_date.replace('-','')
        item_end_date = item_start_date

        file_extent = xml.collection.accession.folder.file[count]['size']
        file_extent = int(file_extent) / 1024
        file_extent = int(file_extent) # get rid of decimals
        file_extent = "Digital file (" + str(file_extent) + " Kb)"

    
        try: # sometimes objects have multiple listings for formats
            file_format = xml.collection.accession.folder.file[count].premis_object.premis_objectCharacteristics.premis_format[0].premis_formatDesignation.premis_formatName.cdata
        except: # sometimes they just have one
            file_format = xml.collection.accession.folder.file[count].premis_object.premis_objectCharacteristics.premis_format.premis_formatDesignation.premis_formatName.cdata

        fixity_note = xml.collection.accession.folder.file[count]['MD5']
        fixity_note = "MD5 checksum: " + fixity_note 
        
        output_file.write(level + "\t" + item_title + "\t" + "\t" + "\t" + item_reference + "\t" + item_start_date + "\t" + item_end_date + "\t"
                          + file_extent + "\t" + file_format + "\t" + "\t" + fixity_note + "\n")

        count += 1
    
    
    
output_file.close()
print ("\nAll operations completed")
