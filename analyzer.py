import unicodecsv
import subprocess
import zipfile
import shapefile
import os, errno
import re
import shutil
import xlrd
import chardet

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
            total = self.do_csv(download)
        else:
            total = self.do_undef(download)

        try:
            download.file_size = os.path.getsize(download.path)
        except TypeError:
            download.file_size = 'undefined'
        download.total = total
        download.dimensions = self.dimensions


    def no_download(self, download):
        if not(download):
            return True
        if not(download.path):
            return True
        return False

    def do_csv(self, download):
        lines = 0
        cols = 0

        if self.no_download(download):
            return 'no download'

        with open(download.path, 'r') as file:
            try:
                dialect = unicodecsv.Sniffer().sniff(file.read(8192)) # Trying to find out the separators
                file.seek(0)
                encoding = chardet.detect(file.read(8192)) # Trying to find out the encoding of the file
                file.seek(0) # Reset to start
                
                reader = unicodecsv.reader(file, dialect, encoding=encoding['encoding'])
                cols = len(reader.next()) # Count the number of columns in the first line
                for j, l in enumerate(file):
                    pass
                lines = j + 1

                self.dimensions['columns'] = cols
                self.dimensions['rows'] = lines
                download.status = "Analyzed"
            
            except Exception as e:
                return "csv exception"

        download.real_format = download.format
        return lines * cols

    def do_axis(self, download):
        
        if self.no_download(download):
            return 'no download'
        
        try:
            arr =  eval(subprocess.check_output(['node', './pcaxis/pc-axis.js', download.path]))
            total = 1
            self.dimensions['dims'] = str(arr)
            for dim in arr:
                total = total * dim

            download.real_format = download.format
            download.status = "Analyzed"
            return total
        except Exception as e:
            return 'axis exception'


    def do_zip(self, download):

        if self.no_download(download):
            return "no download"
        

        total = 0
        total_images = 0
        try:
            with zipfile.ZipFile(download.path, 'r') as myzip:

                files = myzip.namelist()

                img_pattern = re.compile('\.(jpeg|jpg|JPG|JPEG|png|PNG|tif|TIF|tiff|TIFF|gif|GIF)$')
                img_files = len(filter(img_pattern.search, files))
                if(img_files > 0):
                    download.real_format = 'Image'
                    total_images = img_files

                expr = re.compile('\.shp$')
                for shp_name in filter(expr.search, files):
                    
                    # Setting up the tmp dir if necessary
                    try:
                        os.makedirs('tmp')
                    except OSError as e:
                        if e.errno != errno.EEXIST:
                            raise

                    # Extracting all the files to tmp
                    try:
                        myzip.extractall('tmp')
                    except Exception as e :
                        print e
                        return 'zip exception'
                    
                    # Reading the shapefileLCAfood_16080600.nx1
                    try:
                        sf = shapefile.Reader("tmp/"+shp_name)
                    except Exception as e:
                        print e
                        return "shp exception"


                    points = len(sf.records())
                    attributes = len(sf.records()[0])

                    self.dimensions['points'] = points
                    self.dimensions['attributes'] = attributes

                    download.real_format = 'SHP'
                    total = total + (points * attributes)

                    # Remove all the files
                    # TODO: ZIP is extracted multiple times if there is more than one shapefile
                    for the_file in os.listdir('tmp'):
                        file_path = os.path.join('tmp', the_file)
                        try:
                            if os.path.isfile(file_path):
                                os.unlink(file_path)
                            elif os.path.isdir(file_path): shutil.rmtree(file_path)
                        except Exception as e:
                            print(e)

                # Priority goes to Shapefiles. If there are none, return the count of images in the ZIP
                download.status = "Analyzed"
                return total if (download.real_format == 'SHP') else total_images                
        except Exception as general_exception:
            print general_exception
            return 'zip exception'


    def do_xls(self, download):

        if self.no_download(download):
            return "no download"

        try:
            wb = xlrd.open_workbook(download.path)

            total = 0
            self.dimensions['sheets'] = wb.nsheets

            for i in range(0, wb.nsheets):
                cols = wb.sheet_by_index(i).ncols
                rows = wb.sheet_by_index(i).nrows

                self.dimensions['columns'] = cols
                self.dimensions['rows'] = rows

                total = total + (cols * rows)

            download.real_format = "XLS"
            download.status = "Analyzed"
            return total
        except Exception as e:
            print download.path + ": " + str(e)
            return "Excel exception"

    def do_multiformat(self, download):
        try:
            return self.do_zip(download)

        except Exception as e:
            return "Multiformat exception"

    def do_undef(self, download):
        if self.no_download(download):
            return "no download"

        download.real_format = "Other"
        download.status = "Analyzed"
        return 'undefined'
