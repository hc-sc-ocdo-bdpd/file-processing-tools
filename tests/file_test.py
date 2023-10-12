import sys, os
sys.path.append(os.path.join(sys.path[0],'file_processing'))

def test_txt_text():
    from file_processing.file import File
    txt_1 = File('tests/resources/test_files/government_of_canada_wikipedia.txt')
    txt_2 = File('tests/resources/test_files/usa_government_wikipedia.txt')
    assert len(txt_1.metadata['text']) == 38983
    assert len(txt_2.metadata['text']) == 47819

def test_txt_num_lines():
    # indirectly tests lines attribute
    from file_processing.file import File
    txt_1 = File('tests/resources/test_files/government_of_canada_wikipedia.txt')
    txt_2 = File('tests/resources/test_files/usa_government_wikipedia.txt')
    assert txt_1.metadata['num_lines'] == 306
    assert txt_2.metadata['num_lines'] == 383

def test_txt_num_words():
    # indirectly tests words attribute
    from file_processing.file import File
    txt_1 = File('tests/resources/test_files/government_of_canada_wikipedia.txt')
    txt_2 = File('tests/resources/test_files/usa_government_wikipedia.txt')
    assert txt_1.metadata['num_words'] == 5691
    assert txt_2.metadata['num_words'] == 7160

def test_save_txt_metadata():
    from file_processing.file import File
    
    test_txt_path = 'tests/resources/test_files/government_of_canada_wikipedia.txt'
    copy_test_txt_path = 'tests/resources/test_files/government_of_canada_wikipedia_copy.txt'
    
    # Copying file
    with open(test_txt_path, 'rb') as src_file:
        with open(copy_test_txt_path, 'wb') as dest_file:
            dest_file.write(src_file.read())

    try:
        
        # Load via File object
        txt_file = File(copy_test_txt_path)
        
        # Save
        txt_file.save()
        
        # Assert if .txt correctly saved
        assert len(txt_file.metadata['text']) == 38983

    finally:
        # Clean up by removing the copied file after the test is done
        os.remove(copy_test_txt_path)

def test_txt_save_as_pdf():
    from file_processing.file import File

    # Paths of test files
    test_txt_path = 'tests/resources/test_files/government_of_canada_wikipedia.txt'
    output_pdf_path = 'tests/resources/test_files/government_of_canada_wikipedia.pdf'

    try:
        # Convert TXT to PDF
        txt_file = File(test_txt_path)
        txt_file.processor.save_as_pdf(output_pdf_path)
        
        # Verify the PDF file was created and is not empty
        assert os.path.exists(output_pdf_path)
        assert os.path.getsize(output_pdf_path) > 0

    finally:
        # Clean up by removing the PDF file after the test is done
        if os.path.exists(output_pdf_path):
            os.remove(output_pdf_path)

def test_txt_save_as_docx():
    from file_processing.file import File

    # Paths of test files
    test_txt_path = 'tests/resources/test_files/government_of_canada_wikipedia.txt'
    output_docx_path = 'tests/resources/test_files/government_of_canada_wikipedia.docx'

    try:
        # Convert TXT to DOCX
        txt_file = File(test_txt_path)
        txt_file.processor.save_as_docx(output_docx_path)
        
        assert os.path.exists(output_docx_path)
        assert os.path.getsize(output_docx_path) > 0
             

    finally:
        # Clean up by removing the DOCX file after the test is done
        if os.path.exists(output_docx_path):
            os.remove(output_docx_path)

def test_docx_text():
    from file_processing.file import File
    docx_1 = File('tests/resources/test_files/HealthCanadaOverviewFromWikipedia.docx')
    docx_2 = File('tests/resources/test_files/SampleReport.docx')
    assert len(docx_1.metadata['text']) == 1631
    assert len(docx_2.metadata['text']) == 3220


def test_docx_author():
    from file_processing.file import File
    from docx import Document

    # Paths of test files
    test_docx_1_path = 'tests/resources/test_files/HealthCanadaOverviewFromWikipedia.docx'
    test_docx_2_path = 'tests/resources/test_files/SampleReport.docx'

    # Arbitrary test author names
    test_author_1 = 'Test Author One'
    test_author_2 = 'Second Test Author'

    # Update test docx files to have test names
    for x in [(test_docx_1_path,test_author_1), (test_docx_2_path, test_author_2)]:
        doc = Document(x[0])
        doc.core_properties.author = x[1]
        doc.save(x[0])

    # Test author names match
    docx_1 = File(test_docx_1_path)
    docx_2 = File(test_docx_2_path)
    assert docx_1.metadata['author'] == test_author_1
    assert docx_2.metadata['author'] == test_author_2


def test_docx_last_modified_by():
    from file_processing.file import File
    from docx import Document

    # Paths of test files
    test_docx_1_path = 'tests/resources/test_files/HealthCanadaOverviewFromWikipedia.docx'
    test_docx_2_path = 'tests/resources/test_files/SampleReport.docx'

    # Arbitrary test last_modified_by names
    test_last_modified_by_1 = 'Test last_modified_by One'
    test_last_modified_by_2 = 'last_modified_by Test Author'

    # Update test docx files to have test names
    for x in [(test_docx_1_path,test_last_modified_by_1), (test_docx_2_path, test_last_modified_by_2)]:
        doc = Document(x[0])
        doc.core_properties.last_modified_by = x[1]
        doc.save(x[0])

    # Test last_modified_by names match
    docx_1 = File(test_docx_1_path)
    docx_2 = File(test_docx_2_path)
    assert docx_1.metadata['last_modified_by'] == test_last_modified_by_1
    assert docx_2.metadata['last_modified_by'] == test_last_modified_by_2


def test_save_docx_metadata():
    from file_processing.file import File
    from docx import Document
    
    test_docx_path = 'tests/resources/test_files/HealthCanadaOverviewFromWikipedia.docx'
    copy_test_docx_path = 'tests/resources/test_files/HealthCanadaOverviewFromWikipedia_copy.docx'
    
    # Copying file
    with open(test_docx_path, 'rb') as src_file:
        with open(copy_test_docx_path, 'wb') as dest_file:
            dest_file.write(src_file.read())

    try:
        # Arbitrary test author and last_modified_by names
        test_author = 'New Author'
        test_last_modified_by = 'Modified Author'
        
        # Load and change metadata via File object
        docx_file = File(copy_test_docx_path)
        docx_file.metadata['author'] = test_author
        docx_file.metadata['last_modified_by'] = test_last_modified_by
        
        # Save changes
        docx_file.save()
        
        # Load document again to check if the changes were saved correctly
        doc = Document(copy_test_docx_path)
        
        # Assert if changes are correctly reflected
        assert doc.core_properties.author == test_author
        assert doc.core_properties.last_modified_by == test_last_modified_by

    finally:
        # Clean up by removing the copied file after the test is done
        os.remove(copy_test_docx_path)


def test_docx_save_as_txt():
    from file_processing.file import File

    # Paths of test files
    test_docx_path = 'tests/resources/test_files/HealthCanadaOverviewFromWikipedia.docx'
    output_txt_path = 'tests/resources/test_files/HealthCanadaOverviewFromWikipedia_output.txt'

    try:
        # Convert DOCX to TXT
        docx_file = File(test_docx_path)
        docx_file.processor.save_as_txt(output_txt_path)
        
        # Verify the TXT file was created and is not empty
        assert os.path.exists(output_txt_path)
        with open(output_txt_path, 'r', encoding='utf-8') as file:
            txt_content = file.read()
        assert len(txt_content) > 0
        assert txt_content == docx_file.metadata['text']

    finally:
        # Clean up by removing the TXT file after the test is done
        if os.path.exists(output_txt_path):
            os.remove(output_txt_path)

def test_docx_save_as_pdf():
    from file_processing.file import File

    # Paths of test files
    test_docx_path = 'tests/resources/test_files/HealthCanadaOverviewFromWikipedia.docx'
    output_pdf_path = 'tests/resources/test_files/HealthCanadaOverviewFromWikipedia_output.pdf'

    try:
        # Convert DOCX to PDF
        docx_file = File(test_docx_path)
        docx_file.processor.save_as_pdf(output_pdf_path)
        
        # Verify the PDF file was created and is not empty
        assert os.path.exists(output_pdf_path)
        assert os.path.getsize(output_pdf_path) > 0

    finally:
        # Clean up by removing the PDF file after the test is done
        if os.path.exists(output_pdf_path):
            os.remove(output_pdf_path)


def test_pdf_ocr_text_found():
    from file_processing.file import File
    pdf_1 = File('tests/resources/test_files/SampleReportScreenShot.pdf', use_ocr=True)
    ocr_text = pdf_1.metadata['ocr_text']
    assert len(ocr_text) > 0

def test_pdf_save_as_txt():
    from file_processing.file import File

    # Paths of test files
    test_pdf_path = 'tests/resources/test_files/HealthCanadaOverviewFromWikipedia.pdf'
    output_txt_path = 'tests/resources/test_files/HealthCanadaOverviewFromWikipedia.txt'

    try:
        # Convert PDF to TXT
        pdf_file = File(test_pdf_path)
        pdf_file.processor.save_as_txt(output_txt_path)
        
        # Verify the TXT file was created and is not empty
        assert os.path.exists(output_txt_path)
        assert os.path.getsize(output_txt_path) > 0

    finally:
        # Clean up by removing the TXT file after the test is done
        if os.path.exists(output_txt_path):
            os.remove(output_txt_path)
    
def test_pdf_save_as_docx():
    from file_processing.file import File

    # Paths of test files
    test_pdf_path = 'tests/resources/test_files/HealthCanadaOverviewFromWikipedia.pdf'
    output_docx_path = 'tests/resources/test_files/HealthCanadaOverviewFromWikipedia_copy.docx'

    try:
        # Convert PDF to DOCX
        pdf_file = File(test_pdf_path)
        pdf_file.processor.save_as_docx(output_docx_path)
        
        # Verify the DOCX file was created and is not empty
        assert os.path.exists(output_docx_path)
        assert os.path.getsize(output_docx_path) > 0

    finally:
        # Clean up by removing the DOCX file after the test is done
        if os.path.exists(output_docx_path):
            os.remove(output_docx_path)
    
def test_msg_text():
    from file_processing.file import File
    msg = File('tests/resources/test_files/Test Email.msg')
    msg_text = msg.metadata['text']
    assert msg_text == 'Body text.\r\n\r\n \r\n\r\n'

    
def test_msg_subject():
    from file_processing.file import File
    msg = File('tests/resources/test_files/Test Email.msg')
    msg_subject = msg.metadata['subject']
    assert msg_subject == 'Test Email'

    
def test_msg_date():
    from file_processing.file import File
    msg = File('tests/resources/test_files/Test Email.msg')
    msg_date = msg.metadata['date']
    assert msg_date == 'Mon, 18 Sep 2023 13:57:16 -0400'

    
def test_msg_sender():
    from file_processing.file import File
    msg = File('tests/resources/test_files/Test Email.msg')
    msg_sender = msg.metadata['sender']
    assert msg_sender == '"Burnett, Taylen (HC/SC)" <Taylen.Burnett@hc-sc.gc.ca>'

def test_save_msg_metadata():
    from file_processing.file import File

    test_msg_path = 'tests/resources/test_files/Test Email.msg'
    copy_test_msg_path = 'tests/resources/test_files/Test Email_copy.msg'
    
    # Copying file
    with open(test_msg_path, 'rb') as src_file:
        with open(copy_test_msg_path, 'wb') as dest_file:
            dest_file.write(src_file.read())

    try:
        # Load via File object
        msg_file = File(copy_test_msg_path)
        
        # Save changes
        msg_file.save()

        # Load document again to check if the changes were saved correctly
        msg = File(copy_test_msg_path)
        
        # Assert if file correctly saved
        assert msg.metadata['sender'] == '"Burnett, Taylen (HC/SC)" <Taylen.Burnett@hc-sc.gc.ca>'
        assert msg.metadata['date'] == 'Mon, 18 Sep 2023 13:57:16 -0400'
        assert msg.metadata['subject'] == 'Test Email'
        assert msg.metadata['text'] == 'Body text.\r\n\r\n \r\n\r\n'

    finally:
        os.remove(copy_test_msg_path)

def test_msg_save_as_txt():
    from file_processing.file import File

    # Paths of test files
    test_msg_path = 'tests/resources/test_files/Test Email.msg'
    output_txt_path = 'tests/resources/test_files/Test Email.txt'

    try:
        # Convert MSG to TXT
        msg_file = File(test_msg_path)
        msg_file.processor.save_as_txt(output_txt_path)
        
        # Verify the TXT file was created and is not empty
        assert os.path.exists(output_txt_path)
        assert os.path.getsize(output_txt_path) > 0

    finally:
        # Clean up by removing the TXT file after the test is done
        if os.path.exists(output_txt_path):
            os.remove(output_txt_path)

def test_msg_save_as_pdf():
    from file_processing.file import File

    # Paths of test files
    test_msg_path = 'tests/resources/test_files/Test Email.msg'
    output_pdf_path = 'tests/resources/test_files/Test Email.pdf'

    try:
        # Convert MSG to PDF
        msg_file = File(test_msg_path)
        msg_file.processor.save_as_pdf(output_pdf_path)
        
        # Verify the PDF file was created and is not empty
        assert os.path.exists(output_pdf_path)
        assert os.path.getsize(output_pdf_path) > 0

    finally:
        # Clean up by removing the PDF file after the test is done
        if os.path.exists(output_pdf_path):
            os.remove(output_pdf_path)

def test_png_format():
    from file_processing.file import File
    png_1 = File('tests/resources/test_files/Health_Canada_logo.png')
    png_2 = File('tests/resources/test_files/MapCanada.png')
    assert png_1.metadata['original_format'] == 'GIF'
    assert png_2.metadata['original_format'] == 'PNG'

    
def test_png_mode():
    from file_processing.file import File
    png_1 = File('tests/resources/test_files/Health_Canada_logo.png')
    png_2 = File('tests/resources/test_files/MapCanada.png')
    assert png_1.metadata['mode'] == 'P'
    assert png_2.metadata['mode'] == 'RGBA'

    
def test_png_width():
    from file_processing.file import File
    png_1 = File('tests/resources/test_files/Health_Canada_logo.png')
    png_2 = File('tests/resources/test_files/MapCanada.png')
    assert png_1.metadata['width'] == 303
    assert png_2.metadata['width'] == 3000

    
def test_png_height():
    from file_processing.file import File
    png_1 = File('tests/resources/test_files/Health_Canada_logo.png')
    png_2 = File('tests/resources/test_files/MapCanada.png')
    assert png_1.metadata['height'] == 40
    assert png_2.metadata['height'] == 2408

def test_save_png_metadata():
    from file_processing.file import File
    
    test_jpeg_path = 'tests/resources/test_files/Health_Canada_logo.png'
    copy_test_jpeg_path = 'tests/resources/test_files/Health_Canada_logo_copy.png'
    
    # Copying file
    with open(test_jpeg_path, 'rb') as src_file:
        with open(copy_test_jpeg_path, 'wb') as dest_file:
            dest_file.write(src_file.read())

    try:
        # Load via File object
        jpeg_file = File(copy_test_jpeg_path)
        
        # Save changes
        jpeg_file.save()
        
        # Load document again to check if the changes were saved correctly
        jpeg = File(copy_test_jpeg_path)
        
        # Assert if file correctly saved
        assert jpeg.metadata['height'] == 40
        assert jpeg.metadata['width'] == 303
        assert jpeg.metadata['mode'] == 'P'

    finally:
        # Clean up by removing the copied file after the test is done
        os.remove(copy_test_jpeg_path)

def test_png_save_as_pdf():
    from file_processing.file import File

    # Paths of test files
    test_png_path = 'tests/resources/test_files/Health_Canada_logo.png'
    output_pdf_path = 'tests/resources/test_files/Health_Canada_logo.pdf'

    try:
        # Convert JPEG to PDF
        png_file = File(test_png_path)
        png_file.processor.save_as_pdf(output_pdf_path)
        
    # Verify the PDF file was created and is not empty
        assert os.path.exists(output_pdf_path)
        assert os.path.getsize(output_pdf_path) > 0

    finally:
        # Clean up by removing the PDF file after the test is done
        if os.path.exists(output_pdf_path):
            os.remove(output_pdf_path)
    
    
def test_excel_sheets():
    from file_processing.file import File 
    exceldoc = File('tests/resources/test_files/Test_excel_file.xlsx')
    exceldoc_sheetnames = exceldoc.metadata['sheet_names']
    assert exceldoc_sheetnames == ['Sheet1', 'Sheet2', 'Sheet3']

    
def test_excel_activesheet():
    from file_processing.file import File
    exceldoc = File('tests/resources/test_files/Test_excel_file.xlsx')
    exceldoc_activesheet = exceldoc.metadata['active_sheet']
    assert str(exceldoc_activesheet) == "<Worksheet \"Sheet3\">"

    
def test_excel_data():
    from file_processing.file import File
    exceldoc = File('tests/resources/test_files/Test_excel_file.xlsx')
    assert len(exceldoc.metadata['data']['Sheet1']) == 10
    assert len(exceldoc.metadata['data']['Sheet2']) == 11
    assert len(exceldoc.metadata['data']['Sheet3']) == 21

    
def test_excel_last_modified_by():
    from file_processing.file import File
    exceldoc = File('tests/resources/test_files/Test_excel_file.xlsx')
    assert exceldoc.metadata['last_modified_by'] == 'Burnett, Taylen (HC/SC)'

    
def test_excel_creator():
    from file_processing.file import File
    exceldoc = File('tests/resources/test_files/Test_excel_file.xlsx')
    assert exceldoc.metadata['creator'] == 'Burnett, Taylen (HC/SC)'

def test_save_exc_metadata():
    from file_processing.file import File
    from openpyxl import load_workbook
    
    test_exc_path = 'tests/resources/test_files/Test_excel_file.xlsx'
    copy_test_exc_path = 'tests/resources/test_files/Test_excel_file_copy.xlsx'
    
    # Copying file
    with open(test_exc_path, 'rb') as src_file:
        with open(copy_test_exc_path, 'wb') as dest_file:
            dest_file.write(src_file.read())

    try:
        # Arbitrary test author and last_modified_by names
        test_creator = 'New Creator'
        test_last_modified_by = 'Modified Creator'
        
        # Load and change metadata via File object
        exc_file = File(copy_test_exc_path)
        exc_file.metadata['creator'] = test_creator
        exc_file.metadata['last_modified_by'] = test_last_modified_by
        
        # Save changes
        exc_file.save()
        
        # Load document again to check if the changes were saved correctly
        exceldoc = load_workbook(copy_test_exc_path)
        
        # Assert if changes are correctly reflected
        assert exceldoc.properties.creator == test_creator
        assert exceldoc.properties.lastModifiedBy == test_last_modified_by

    finally:
        # Clean up by removing the copied file after the test is done
        os.remove(copy_test_exc_path)
    
def test_pptx_text():
    from file_processing.file import File
    pptx_1 = File('tests/resources/test_files/HealthCanadaOverviewFromWikipedia.pptx')
    pptx_2 = File('tests/resources/test_files/SampleReport.pptx')
    assert len(pptx_1.metadata['text']) == 1655
    assert len(pptx_2.metadata['text']) == 2037


def test_pptx_author():
    from file_processing.file import File
    from pptx import Presentation

    # Paths of test files
    test_pptx_1_path = 'tests/resources/test_files/HealthCanadaOverviewFromWikipedia.pptx'
    test_pptx_2_path = 'tests/resources/test_files/SampleReport.pptx'

    # Arbitrary test author names
    test_author_1 = 'Test Author One'
    test_author_2 = 'Second Test Author'

    # Update test pptx files to have test names
    for x in [(test_pptx_1_path,test_author_1), (test_pptx_2_path, test_author_2)]:
        ppt = Presentation(x[0])
        ppt.core_properties.author = x[1]
        ppt.save(x[0])

    # Test author names match
    pptx_1 = File(test_pptx_1_path)
    pptx_2 = File(test_pptx_2_path)
    assert pptx_1.metadata['author'] == test_author_1
    assert pptx_2.metadata['author'] == test_author_2


def test_pptx_last_modified_by():
    from file_processing.file import File
    from pptx import Presentation

    # Paths of test files
    test_pptx_1_path = 'tests/resources/test_files/HealthCanadaOverviewFromWikipedia.pptx'
    test_pptx_2_path = 'tests/resources/test_files/SampleReport.pptx'

    # Arbitrary test last_modified_by names
    test_last_modified_by_1 = 'Test last_modified_by One'
    test_last_modified_by_2 = 'last_modified_by Test Author'

    # Update test pptx files to have test names
    for x in [(test_pptx_1_path,test_last_modified_by_1), (test_pptx_2_path, test_last_modified_by_2)]:
        ppt = Presentation(x[0])
        ppt.core_properties.last_modified_by = x[1]
        ppt.save(x[0])

    # Test last_modified_by names match
    pptx_1 = File(test_pptx_1_path)
    pptx_2 = File(test_pptx_2_path)
    assert pptx_1.metadata['last_modified_by'] == test_last_modified_by_1
    assert pptx_2.metadata['last_modified_by'] == test_last_modified_by_2

    
def test_pptx_num_slides():
    from file_processing.file import File
    pptx_1 = File('tests/resources/test_files/HealthCanadaOverviewFromWikipedia.pptx')
    pptx_2 = File('tests/resources/test_files/SampleReport.pptx')
    assert pptx_1.metadata['num_slides'] == 4
    assert pptx_2.metadata['num_slides'] == 5

def test_save_ppt_metadata():
    from file_processing.file import File
    from pptx import Presentation
    test_ppt_path = 'tests/resources/test_files/HealthCanadaOverviewFromWikipedia.pptx'
    copy_test_ppt_path = 'tests/resources/test_files/HealthCanadaOverviewFromWikipedia_copy.pptx'
    
    # Copying file
    with open(test_ppt_path, 'rb') as src_file:
        with open(copy_test_ppt_path, 'wb') as dest_file:
            dest_file.write(src_file.read())

    try:
        # Arbitrary test author and last_modified_by names
        test_author = 'New Author'
        test_last_modified_by = 'Modified Author'
        
        # Load and change metadata via File object
        ppt_file = File(copy_test_ppt_path)
        ppt_file.metadata['author'] = test_author
        ppt_file.metadata['last_modified_by'] = test_last_modified_by
        
        # Save changes
        ppt_file.save()
        
        # Load document again to check if the changes were saved correctly
        ppt = Presentation(copy_test_ppt_path)
        
        # Assert if changes are correctly reflected
        assert ppt.core_properties.author == test_author
        assert ppt.core_properties.last_modified_by == test_last_modified_by

    finally:
        # Clean up by removing the copied file after the test is done
        os.remove(copy_test_ppt_path)

def test_pptx_save_as_pdf():
    from file_processing.file import File

    # Paths of test files
    test_html_path = 'tests/resources/test_files/HealthCanadaOverviewFromWikipedia.pptx'
    output_txt_path = 'tests/resources/test_files/_HealthCanadaOverviewFromWikipedia_.pdf'
    try:
        # Convert PPTX to PDF
        html_file = File(test_html_path)
        html_file.processor.save_as_pdf(output_txt_path)
        
    # Verify the PDF file was created and is not empty
        assert os.path.exists(output_txt_path)
        assert os.path.getsize(output_txt_path) > 0

    finally:
        # Clean up by removing the PDF file after the test is done
        if os.path.exists(output_txt_path):
            os.remove(output_txt_path)
    
def test_rtf_text():
    from file_processing.file import File
    rtf_1 = File('tests/resources/test_files/Test_for_RTF.rtf')
    assert len(rtf_1.metadata['text']) == 5306

def test_save_rtf_metadata():
    from file_processing.file import File
    
    test_rtf_path = 'tests/resources/test_files/Test_for_RTF.rtf'
    copy_test_rtf_path = 'tests/resources/test_files/Test_for_RTF_copy.rtf'
    
    # Copying file
    with open(test_rtf_path, 'rb') as src_file:
        with open(copy_test_rtf_path, 'wb') as dest_file:
            dest_file.write(src_file.read())

    try:
        
        # Load via File object
        rtf_file = File(copy_test_rtf_path)
        
        # Save
        rtf_file.save()
        
        # Assert if .txt correctly saved
        assert len(rtf_file.metadata['text']) == 5306

    finally:
        # Clean up by removing the copied file after the test is done
        os.remove(copy_test_rtf_path)

def test_rtf_save_as_txt():
    from file_processing.file import File

    # Paths of test files
    test_rtf_path = 'tests/resources/test_files/Test_for_RTF.rtf'
    output_txt_path = 'tests/resources/test_files/Test_for_RTF.txt'

    try:
        # Convert RTF to TXT
        rtf_file = File(test_rtf_path)
        rtf_file.processor.save_as_txt(output_txt_path)
        
    # Verify the TXT file was created and is not empty
        assert os.path.exists(output_txt_path)
        assert os.path.getsize(output_txt_path) > 0

    finally:
        # Clean up by removing the TXT file after the test is done
        if os.path.exists(output_txt_path):
            os.remove(output_txt_path)

def test_rtf_save_as_docx():
    from file_processing.file import File

    # Paths of test files
    test_rtf_path = 'tests/resources/test_files/Test_for_RTF.rtf'
    output_docx_path = 'tests/resources/test_files/Test_for_RTF.docx'

    try:
        # Convert RTF to DOCX
        rtf_file = File(test_rtf_path)
        rtf_file.processor.save_as_docx(output_docx_path)
        
    # Verify the DOCX file was created and is not empty
        assert os.path.exists(output_docx_path)
        assert os.path.getsize(output_docx_path) > 0

    finally:
        # Clean up by removing the DOCX file after the test is done
        if os.path.exists(output_docx_path):
            os.remove(output_docx_path)
                 
def test_html_text():
    from file_processing.file import File
    txt_1 = File('tests/resources/test_files/Health - Canada.ca.html')
    assert len(txt_1.metadata['text']) == 165405

    
def test_html_num_lines():
    # indirectly tests lines attribute
    from file_processing.file import File
    txt_1 = File('tests/resources/test_files/Health - Canada.ca.html')
    assert txt_1.metadata['num_lines'] == 3439

    
def test_html_num_words():
    # indirectly tests words attribute
    from file_processing.file import File
    txt_1 = File('tests/resources/test_files/Health - Canada.ca.html')
    assert txt_1.metadata['num_words'] == 11162

def test_save_html_metadata():
    from file_processing.file import File
    
    test_html_path = 'tests/resources/test_files/Health - Canada.ca.html'
    copy_test_html_path = 'tests/resources/test_files/Health - Canada.ca_copy.html'
    
    # Copying file
    with open(test_html_path, 'rb') as src_file:
        with open(copy_test_html_path, 'wb') as dest_file:
            dest_file.write(src_file.read())

    try:
        
        # Load via File object
        html_file = File(copy_test_html_path)
        
        # Save
        html_file.save()
        
        # Assert if .txt correctly saved
        assert len(html_file.metadata['text']) == 165405

    finally:
        # Clean up by removing the copied file after the test is done
        os.remove(copy_test_html_path)

def test_html_save_as_txt():
    from file_processing.file import File

    # Paths of test files
    test_html_path = 'tests/resources/test_files/Health - Canada.ca.html'
    output_txt_path = 'tests/resources/test_files/Health - Canada.ca.txt'
    try:
        # Convert HTML to TXT
        html_file = File(test_html_path)
        html_file.processor.save_as_txt(output_txt_path)
        
    # Verify the TXT file was created and is not empty
        assert os.path.exists(output_txt_path)
        assert os.path.getsize(output_txt_path) > 0

    finally:
        # Clean up by removing the TXT file after the test is done
        if os.path.exists(output_txt_path):
            os.remove(output_txt_path)

    
def test_xml_text():
    from file_processing.file import File
    txt_1 = File('tests/resources/test_files/Sample.xml')
    assert len(txt_1.metadata['text']) == 4429

    
def test_xml_num_lines():
    # indirectly tests lines attribute
    from file_processing.file import File
    txt_1 = File('tests/resources/test_files/Sample.xml')
    assert txt_1.metadata['num_lines'] == 120

    
def test_xml_num_words():
    # indirectly tests words attribute
    from file_processing.file import File
    txt_1 = File('tests/resources/test_files/Sample.xml')
    assert txt_1.metadata['num_words'] == 336

def test_save_xml_metadata():
    from file_processing.file import File
    
    test_xml_path = 'tests/resources/test_files/Sample.xml'
    copy_test_xml_path = 'tests/resources/test_files/Sample_copy.xml'
    
    # Copying file
    with open(test_xml_path, 'rb') as src_file:
        with open(copy_test_xml_path, 'wb') as dest_file:
            dest_file.write(src_file.read())

    try:
        
        # Load via File object
        xml_file = File(copy_test_xml_path)
        
        # Save
        xml_file.save()
        
        # Assert if .txt correctly saved
        assert len(xml_file.metadata['text']) == 4429

    finally:
        # Clean up by removing the copied file after the test is done
        os.remove(copy_test_xml_path)

def test_jpeg_format():
    from file_processing.file import File
    jpeg_1 = File('tests/resources/test_files/HealthCanada.jpeg')
    jpeg_2 = File('tests/resources/test_files/MapCanada.jpg')
    assert jpeg_1.metadata['original_format'] == 'JPEG'
    assert jpeg_2.metadata['original_format'] == 'JPEG'

    
def test_jpeg_mode():
    from file_processing.file import File
    jpeg_1 = File('tests/resources/test_files/HealthCanada.jpeg')
    jpeg_2 = File('tests/resources/test_files/MapCanada.jpg')
    assert jpeg_1.metadata['mode'] == 'RGB'
    assert jpeg_2.metadata['mode'] == 'RGB'

    
def test_jpeg_width():
    from file_processing.file import File
    jpeg_1 = File('tests/resources/test_files/HealthCanada.jpeg')
    jpeg_2 = File('tests/resources/test_files/MapCanada.jpg')
    assert jpeg_1.metadata['width'] == 474
    assert jpeg_2.metadata['width'] == 4489

    
def test_jpeg_height():
    from file_processing.file import File
    jpeg_1 = File('tests/resources/test_files/HealthCanada.jpeg')
    jpeg_2 = File('tests/resources/test_files/MapCanada.jpg')
    assert jpeg_1.metadata['height'] == 262
    assert jpeg_2.metadata['height'] == 2896

def test_save_jpeg_metadata():
    from file_processing.file import File
    
    test_jpeg_path = 'tests/resources/test_files/HealthCanada.jpeg'
    copy_test_jpeg_path = 'tests/resources/test_files/HealthCanada_copy.jpeg'
    
    # Copying file
    with open(test_jpeg_path, 'rb') as src_file:
        with open(copy_test_jpeg_path, 'wb') as dest_file:
            dest_file.write(src_file.read())

    try:
        # Load via File object
        jpeg_file = File(copy_test_jpeg_path)
        
        # Save changes
        jpeg_file.save()
        
        # Load document again to check if the changes were saved correctly
        jpeg = File(copy_test_jpeg_path)
        
        # Assert if file correctly saved
        assert jpeg.metadata['height'] == 262
        assert jpeg.metadata['width'] == 474
        assert jpeg.metadata['mode'] == 'RGB'

    finally:
        # Clean up by removing the copied file after the test is done
        os.remove(copy_test_jpeg_path)

def test_jpeg_save_as_pdf():
    from file_processing.file import File

    # Paths of test files
    test_jpeg_path = 'tests/resources/test_files/HealthCanada.jpeg'
    output_pdf_path = 'tests/resources/test_files/HealthCanada_.pdf'

    try:
        # Convert JPEG to PDF
        jpeg_file = File(test_jpeg_path)
        jpeg_file.processor.save(output_pdf_path)
        
    # Verify the PDF file was created and is not empty
        assert os.path.exists(output_pdf_path)
        assert os.path.getsize(output_pdf_path) > 0

    finally:
        # Clean up by removing the PDF file after the test is done
        if os.path.exists(output_pdf_path):
            os.remove(output_pdf_path)