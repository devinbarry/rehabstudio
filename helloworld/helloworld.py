import os

import jinja2
import webapp2
import lib.cloudstorage as gcs
from google.appengine.api import app_identity

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class MainPage(webapp2.RequestHandler):
    def get(self):
        bucket_name = os.environ.get('BUCKET_NAME', app_identity.get_default_gcs_bucket_name())

        bucket_list = self.get_bucket_list('/' + bucket_name)
        file_names = [file.filename for file in bucket_list]
        file_names = [part.split('/')[-1] for part in file_names]
        root = 'https://storage.cloud.google.com/devinbarry.appspot.com/'
        file_names = [root + file_name for file_name in file_names]

        # 'https://storage.cloud.google.com/devinbarry.appspot.com/Carpaccio.jpg'

        template_values = {'imageUrl': 'test', 'file_names': file_names}
        template = JINJA_ENVIRONMENT.get_template('templates/images.html')
        self.response.write(template.render(template_values))

    def get_bucket_list(self, bucket):
        bucket_list = []
        page_size = 100
        stats = gcs.listbucket(bucket, max_keys=page_size)
        while True:
            count = 0
            for stat in stats:
                count += 1
                bucket_list.append(stat)

            if count != page_size or count == 0:
                break
            stats = gcs.listbucket(bucket, max_keys=page_size,
                                   marker=stat.filename)
        return bucket_list


class CloudStorage(webapp2.RequestHandler):
    def get(self):
        bucket_name = os.environ.get('BUCKET_NAME', app_identity.get_default_gcs_bucket_name())

        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Demo GCS Application running from Version: '
                            + os.environ['CURRENT_VERSION_ID'] + '\n')
        self.response.write('Using bucket name: ' + bucket_name + '\n\n')


class ListBucket(webapp2.RequestHandler):
    def get(self):
        bucket_name = os.environ.get('BUCKET_NAME', app_identity.get_default_gcs_bucket_name())
        self.list_bucket(bucket='/' + bucket_name)

    def list_bucket(self, bucket):
        """Create several files and paginate through them.

        Production apps should set page_size to a practical value.

        Args:
          bucket: bucket.
        """
        self.response.write('Listbucket result:\n')

        page_size = 1
        stats = gcs.listbucket(bucket, max_keys=page_size)
        while True:
            count = 0
            for stat in stats:
                count += 1
                self.response.write(repr(stat))
                self.response.write('\n')

            if count != page_size or count == 0:
                break
            stats = gcs.listbucket(bucket, max_keys=page_size,
                                   marker=stat.filename)


class Upload(webapp2.RequestHandler):
    def get(self):
        template_values = {'imageUrl': 'test'}

        template = JINJA_ENVIRONMENT.get_template('templates/upload.html')
        self.response.write(template.render(template_values))

    def post(self):
        # app_default_bucket
        bucket_name = os.environ.get('BUCKET_NAME', app_identity.get_default_gcs_bucket_name())
        image = self.request.get('image')

        # Use uuid4() here to make file names unique if needed
        file_name = self.request.params['image'].filename
        self.create_file('/' + bucket_name + '/' + file_name, image)
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Complete!')

    def create_file(self, filename, file_data):
        """Create a file.

        The retry_params specified in the open call will override the default
        retry params for this particular file handle.

        Args:
          filename: filename.
        """
        self.response.write('Creating file %s\n' % filename)
        write_retry_params = gcs.RetryParams(backoff_factor=1.1)
        gcs_file = gcs.open(filename, 'w', retry_params=write_retry_params)
        gcs_file.write(file_data)
        gcs_file.close()


application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/info', CloudStorage),
    ('/list', ListBucket),
    ('/upload', Upload),
], debug=True)


def main():
    application.run()

if __name__ == "__main__":
    main()
