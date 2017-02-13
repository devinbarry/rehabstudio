# rehabstudio
Rehab studio test

### Notes about this code:


### Caveats

1. Tested only in the latest Chrome. Might not work anywhere else.

2. Unused urls/views still in project.


### How to use


https://devinbarry.appspot.com/upload allows you to upload an image (or any other type of file).
A Check box allows you to choose if this image should be public or not

When an image uploads successfully you get a success page.

https://devinbarry.appspot.com/ displays all public images and also shows you your own private images.
It tries to display other kinds of files too. This obviously doesnt work. This page forces you to login


## Improvements

1. Prevent uploading/remove files that are not images
2. Filter output display so that only images are displayed
3. Use the GCS URL functions rather than rolling my own
4. Resize images for fast page loading
