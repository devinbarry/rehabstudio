"use strict";

let app;
// Create a new angular module
app = angular.module('rehab.test', ['ngResource', 'ngSanitize', 'ui.bootstrap', 'ngRoute']);

app.controller('MainController', [
    '$scope', '$interval', '$http', '$route', '$routeParams', '$location',
    function ($scope, $interval, $http, $route, $routeParams, $location) {
        $http.defaults.headers.common['x-auth-token'] = '3G30nCuuQa39jVNEgyrMdw4mKnbHhnORAmkOmsXH0EE=';

        // Init internal variables
        $scope.editForm = {
            imageFileNames: [],
            attachmentFileNames: [],
            intro: '',
        };

        let createEmptyArticle = function(product_hostname) {
            $scope.article = {
                title: "",
                subtitle: "",
                intro: [],
                status: "published",
                premium: false,
                body: [],
                product: product_hostname,
                attachments: [],
                videos: [],
                author: "",
                tags: {},
                keywords: [],
                linked_products: [],
                related_articles: [],
                images: [],
                sections: [],
                properties: {kiosk_type: "article"},
                published_at: new Date().toISOString(),
            };
        };

        // Parse the HTML from SummerNote and convert it into Kiosk format body
        $scope.updateBody = function() {
            try {
                $scope.article.body = new BodyParser($scope.rawBodyText).parse();
            } catch (err) {
                $scope.bodyMessage = err.toString();
            }
        };

        if ('id' in $location.search()) {
            $scope.articleid = $location.search()['id'];
            Article.get({id: $scope.articleid}, function (dataElements) {
                // Update the Product/Section service immediately with raw data
                ProductSectionService.updateProduct(dataElements.product);
                ProductSectionService.updateSectionIDs(dataElements.sections);

                $scope.article = dataElements;

                // If there is dateline information, load it in the editForm
                if (dataElements.tags.dateline) {
                    $scope.editForm.dateline = dataElements.tags.dateline[0];
                }
                // Fetch the intro and body from the article and load them into the form (naive)
                $scope.editForm.intro = $scope.article.intro[0].p;

                // Set the body in the editor correctly
                // TODO write a full unparser that supports all the tags
                $scope.rawBodyText = '';
                for (let bp of $scope.article.body) {
                    if (bp.hasOwnProperty('p')) {
                        $scope.rawBodyText += '<p>' + bp.p + '</p>';
                    }
                }

                // Update the article intro list when new things are entered into the form
                $scope.$watch('editForm["intro"]', function (newValue, oldValue, scope) {
                    // Setup the new style intro paragraphs
                    scope.article.intro = [{'p': newValue}];
                });

                // Add all images to the image button list
                for (let i = 0; i < $scope.article.images.length; i++) {
                    // We don't have a file name thus we use the file format with a sequence number
                    $scope.editForm.imageFileNames.push($scope.article.images[i].format + ' ' + (i+1));
                }

                // Add all attachments to the attachment button list
                for (let i = 0; i < $scope.article.attachments.length; i++) {
                    $scope.editForm.attachmentFileNames.push('attachment' + (i+1));
                }
            });
        } else {
            createEmptyArticle('');
            // Update the article intro list when new things are entered into the form
            $scope.$watch('editForm["intro"]', function (newValue, oldValue, scope) {
                // Setup the new style intro paragraphs
                scope.article.intro = [{'p': newValue}];
            });
        }

        $scope.pagination = {
            totalItems: 0,
            page: 1,
            maxSize: 10
        };

        $scope.submit = function() {
            if ($scope.editForm.dateline) {
                $scope.article.tags.dateline = [$scope.editForm.dateline];
            }

            $http.post('/editor/format-body/', $scope.rawBodyText, {headers: {'Content-Type': 'text/html'}})
                .then(function (response) {
                    $scope.bodyMessage = "";
                    console.log(response.data);
                    $scope.article.body = response.data;

                    let payload = {
                        status: "published",
                        title: $scope.article.title,
                        body: $scope.article.body,
                        premium: $scope.article.premium,
                        product: $scope.article.product,
                        subtitle: $scope.article.subtitle,
                        attachments: $scope.article.attachments,
                        videos: $scope.article.videos,
                        author: $scope.article.author,
                        tags: $scope.article.tags,
                        keywords: $scope.article.keywords,
                        intro: $scope.article.intro,
                        linked_products: [],
                        related_articles: [],
                        images: $scope.article.images,
                        // We need a list of integers
                        sections: $scope.article.sections.map(function(x) { return parseInt(x); }),
                        properties: $scope.article.properties,
                        published_at: $scope.articleid ? $scope.article.published_at : new Date().toISOString(),
                        updated_at: $scope.articleid ? $scope.article.updated_at : new Date().toISOString(),
                    };
                    $("#process-busy-modal").modal("show");

                    if ($scope.articleid) {
                        Article.update({id: $scope.articleid}, payload, function (response) {
                            $("#process-busy-modal").modal("hide");
                            $scope.message = response;
                            window.location.href = 'editor/edit/?id=' + $scope.message.id;
                        }, function (response) {
                            $("#process-busy-modal").modal("hide");
                            $scope.errorMessage = JSON.stringify(response.data);
                        });
                    } else {
                        Article.save(payload, function (response) {
                            $("#process-busy-modal").modal("hide");
                            $scope.message = response;
                            window.location.href = 'editor/edit/?id=' + $scope.message.id;
                        }, function (response) {
                            $("#process-busy-modal").modal("hide");
                            $scope.errorMessage = JSON.stringify(response.data);
                        });
                    }
                }, function (response) {
                    $scope.bodyMessage = JSON.stringify(response.data);
                });
        };
    }
]);
