import os

import jinja2
import webapp2
import uuid
import lib.cloudstorage as gcs
from google.appengine.api import users
from google.appengine.api import app_identity
from google.appengine.ext import ndb


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class UploadedImage(ndb.Model):
    """Data about uploaded images."""
    url = ndb.StringProperty(indexed=False)
    email = ndb.StringProperty(indexed=True)
    public = ndb.BooleanProperty()


class LoginMixin(object):

    def show_login(self):
        login_url = users.create_login_url('/')
        login_link = '<a href="{}">Sign in</a>'.format(login_url)
        self.response.write(login_link)


class MainPage(webapp2.RequestHandler, LoginMixin):
    def get(self):
        user = users.get_current_user()
        if user:
            nickname = user.nickname()
            logout_url = users.create_logout_url('/')
            image_urls = self._get_image_urls(user.email())
            template_values = {'user_nick': nickname, 'logout_url': logout_url}
            template_values.update(image_urls)
            template = JINJA_ENVIRONMENT.get_template('templates/images.html')
            self.response.write(template.render(template_values))
        else:
            self.show_login()

    def _get_image_urls(self, user_email):
        """
        Image urls and information about private and public images are stored in the UploadedImage
        model. We fetch private images for the current user and all public images and create a list
        of image URLs.
        :param user_email:
        :return:
        """
        private_images = UploadedImage.query(UploadedImage.email == user_email, UploadedImage.public == False).fetch()
        public_images = UploadedImage.query(UploadedImage.public == True).fetch()
        public_urls = [image.url for image in public_images]
        private_urls = [image.url for image in private_images]
        return {'public_urls': public_urls, 'private_urls': private_urls}


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

        page_size = 100
        stats = gcs.listbucket(bucket, max_keys=page_size)
        while True:
            count = 0
            for stat in stats:
                count += 1
                self.response.write(repr(stat))
                self.response.write('\n')

            if count != page_size or count == 0:
                break
            stats = gcs.listbucket(bucket, max_keys=page_size, marker=stat.filename)


class Upload(webapp2.RequestHandler, LoginMixin):
    def get(self):
        user = users.get_current_user()
        if user:
            nickname = user.nickname()
            logout_url = users.create_logout_url('/')
            template_values = {'user_nick': nickname, 'logout_url': logout_url}
            template = JINJA_ENVIRONMENT.get_template('templates/upload.html')
            self.response.write(template.render(template_values))
        else:
            self.show_login()

    def post(self):
        user = users.get_current_user()
        if user:
            # app_default_bucket
            bucket_name = os.environ.get('BUCKET_NAME', app_identity.get_default_gcs_bucket_name())
            image = self.request.get('image')
            public = self.request.POST.get('public-checkbox', None)

            check_box = False
            if public is not None:
                check_box = True

            file_name = self.request.params['image'].filename
            # Make file name unique
            name, extension = file_name.rsplit('.', 1)
            file_name = '{}-{}.{}'.format(name, uuid.uuid4(), extension)

            self._upload_to_gcs('/' + bucket_name + '/' + file_name, image, check_box=check_box)
            self._store_image_data(file_name, check_box, user.email())
            self.response.headers['Content-Type'] = 'text/plain'
            self.response.write('Complete!')
        else:
            self.show_login()

    @staticmethod
    def _store_image_data(file_name, public, user_email):
        root = 'https://storage.cloud.google.com/devinbarry.appspot.com/'
        url = root + file_name
        i = UploadedImage(url=url, email=user_email, public=public)
        i.put()

    def _upload_to_gcs(self, bucket_url, file_data, check_box):
        """Create a file.

        The retry_params specified in the open call will override the default
        retry params for this particular file handle.

        Args:
          bucket_url: filename on GCS.
          file_data: raw file data.
          check_box: boolean showing status of the checkbox in the form.
        """
        self.response.write('Creating file %s\n' % bucket_url)
        write_retry_params = gcs.RetryParams(backoff_factor=1.1)
        options = {'x-goog-acl': 'public-read', 'x-goog-meta-public': str(check_box)}
        gcs_file = gcs.open(bucket_url, 'w', options=options, retry_params=write_retry_params)
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
