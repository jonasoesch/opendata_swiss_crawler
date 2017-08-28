import unicodecsv
import subprocess
import zipfile
import shapefile
import os, errno
import re
import shutil

class Analyzer:

    def __init__(self):
        self.dimensions = {}

    def analyze(self, download):

        total = None

        if(download.format == 'CSV'):
            total = self.do_csv(download)
        elif(download.format == "PC-AXIS"):
            total = self.do_axis(download)
        elif(download.format == 'ZIP'):
            total = self.do_zip(download)
        elif(download.format == 'XLS'):
            total = self.do_xls(download)
        elif(download.format == 'MULTIFORMAT'):
            total = self.do_multiformat(download)
        elif(download.format == 'tab-separated-values'):
            total = self.do_tsv(download)
        else:
            total = self.do_undef(download)

        download.file_size = os.path.getsize(download.path)
        download.total = total
        download.dimensions = self.dimensions

        if total != 'undefined' or total != '' or total != 'undefined':
            download.status = "Analyzed"

        #download['fields'] = total
        #download['dimensions'] = self.dimensions



    def do_csv(self, download):
        lines = 0
        cols = 0
        with open(download.path, 'r') as file:
            try:
                dialect = unicodecsv.Sniffer().sniff(file.read(8192))
                file.seek(0)
                reader = unicodecsv.reader(file, dialect)
                cols = len(reader.next())
                for j, l in enumerate(file):
                    pass
                lines = j + 1

                self.dimensions['columns'] = cols
                self.dimensions['rows'] = lines

            except Exception as e:
                print e
                return 'csv exception'
        return lines * cols

    def do_axis(self, download):
        try:
            arr =  eval(subprocess.check_output(['node', '/Users/jonas/Desktop/analyzer/pc-axis.js', download.path]))
            total = 1
            self.dimensions['dims'] = str(arr)
            for dim in arr:
                total = total * dim
            return total
        except Exception as e:
            print e
            return 'axis exception'

    def do_zip(self, download):
        try:
            with zipfile.ZipFile(download.path, 'r') as myzip:
                for zipname in myzip.namelist():
                    if re.search('\.shp$', zipname) != None:
                        try:
                            os.makedirs('tmp')
                        except OSError as e:
                            if e.errno != errno.EEXIST:
                                raise


                        try:
                            myzip.extractall('tmp')
                            sf = shapefile.Reader("tmp/"+zipname)
                        except Exception as e :
                            print e
                            return 'zip exception'
                        points = len(sf.records())
                        attributes = len(sf.records()[0])

                        self.dimensions['points'] = points
                        self.dimensions['attributes'] = attributes

                        return points * attributes


                    for the_file in os.listdir('tmp'):
                        file_path = os.path.join('tmp', the_file)
                        try:
                            if os.path.isfile(file_path):
                                os.unlink(file_path)
                            elif os.path.isdir(file_path): shutil.rmtree(file_path)
                        except Exception as e:
                            print(e)
        except Exception as general_exception:
            print general_exception
            return 'zip exception'

    def do_xls(self, download):

        copy_path = download.path + '.xlsx'
        try:
            shutil.copy(download.path, copy_path)
        except Exception as e:
            return "copying Excel failed"

        try:
            wb = load_workbook(copy_path, read_only=True)

            total = 0
            self.dimensions['sheets'] = len(wb.get_sheet_names())
            for sheet in wb.get_sheet_names():
                cols = wb[sheet].max_column
                rows = wb[sheet].max_row

                self.dimensions['columns'] = cols
                self.dimensions['rows'] = rows

                total = total + (cols * rows)

            os.remove(copy_path)

            return total
        except Exception as e:
            os.remove(copy_path)
            print download.path + ": " + str(e)
            return "Excel exception"

    def do_multiformat(self, download):
        try:
            return self.do_zip(download)

        except Exception as e:
            print download.path + ': ' + str(e)

    def do_undef(self, download):
        return 'undefined'

    def do_tsv(self, download):
        lines = 0
        cols = 0
        with open(download.path, 'r') as file:
            try:
                reader = unicodecsv.reader(file, dialect='excel-tab')
                cols = len(reader.next())
                for j, l in enumerate(file):
                    pass
                lines = j + 1

                self.dimensions['columns'] = cols
                self.dimensions['rows'] = lines

            except Exception as e:
                print e
                return 'tsv exception'
            return lines * cols
