# rehabstudio
Rehab studio test

### Notes about this code:


I have not implemented the public/private stuff and would need to play around more with setting permissions on files I save in GCS.
To get this feature working I would probably need to read permissions for each image (which may involve storing them first) to determine
which user own which image.

The assignment requests "Use Cloud Datastore with the NDB client to store details of the image". I imagine this part was intended to store
which user uploaded which image? I have not implemented this as mentioned above.


### Caveats

1. Tested only in the latest Chrome. Might not work anywhere else.

2. Copied a bunch of angular templates I had written for another project. Thats why the CSS and maybe other places have code that looks out of place.

3. Unused urls/views still in project.


### How to use


https://devinbarry.appspot.com/upload allows you to upload an image (or any other type of file)
These images are set to public

When an image uploads successfully you get a success page.

https://devinbarry.appspot.com/ displays all images uploaded. Tries to display other kinds of files too.
This obviously doesnt work. This page forces you to login


## Improvements

1. Allow uploading files with duplicate names by using UUID
2. Prevent uploading/remove files that are not images
3. Filter output display so that only images are displayed
4. Remove hardcoding of image URL
5. Resize images for fast page loading





