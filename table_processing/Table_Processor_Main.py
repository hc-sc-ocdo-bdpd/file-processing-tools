from Table_Detector import Table_Detector
import logging
logging.basicConfig(filename='table_detection.log', filemode='a', datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO, format='[%(asctime)s][%(levelname)s] %(message)s\n')
logging.getLogger().addHandler(logging.StreamHandler())


logging.info("Table Processor started")
file_path = input('Please enter the path to the PDF to extract tables from: ')
file_path = file_path.replace('\"', '').replace('\\', '\\\\').split('.')[0]
pdf_input = file_path+'.pdf'
xlsx_output = file_path+'.xlsx'
logging.info("Processing " + pdf_input)

try:
    detector = Table_Detector(file = pdf_input)
    logging.info("Saving output to " + xlsx_output)
    detector.to_excel(filename = xlsx_output)
except Exception as e:  # could not detect table from pdf
    logging.error('An error occured while processing ' + file_path + '.')
    logging.error(e)

logging.info("Table Processor finished")
