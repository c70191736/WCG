// Function to extract CSRF token from cookies
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Check if the cookie name matches the expected format
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Function to escape HTML tags
function escapeHtml(html) {
    return html.replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

$(document).ready(function() {
    $('#generate-code-form').submit(function(e) {
        e.preventDefault();
        var formData = $(this).serialize();
        var csrftoken = getCookie('csrftoken'); // Get CSRF token from cookies

        // Show pre-loader and disable button
        $('#generate-code-btn').prop('disabled', true);
        $('#generate-code-text').hide();
        $('#generate-code-loader').show();

        $.ajax({
            type: 'POST',
            url: '/generate_codes/',
            data: formData,
            beforeSend: function(xhr) {
                xhr.setRequestHeader('X-CSRFToken', csrftoken); // Set CSRF token in request headers
            },
            success: function(response) {
                // Hide pre-loader and enable button
                $('#generate-code-btn').prop('disabled', false);
                $('#generate-code-text').show();
                $('#generate-code-loader').hide();

                if (response.hasOwnProperty('error_message')) {
                    $('#code-display').html('<p>Error: ' + response.error_message + '</p>');
                } else {
                    var htmlCode = response.html_code || '';
                    var cssCode = response.css_code || '';
                    var jsCode = response.js_code || '';
                    var externalCssContent = response.external_css_content || {};
                    var externalJsContent = response.external_js_content || {};

                    var displayHtml = '<h2>HTML:</h2><pre>' + escapeHtml(htmlCode) + '</pre>';
                    var displayCss = '<h2>CSS:</h2><pre>' + cssCode + '</pre>';
                    var displayJs = '<h2>JavaScript:</h2><pre>' + jsCode + '</pre>';

                    var displayExternalCss = '';
                    for (var cssUrl in externalCssContent) {
                        displayExternalCss += '<h2>CSS file: ' + cssUrl + '</h2><pre>' + externalCssContent[cssUrl] + '</pre>';
                    }

                    var displayExternalJs = '';
                    for (var jsUrl in externalJsContent) {
                        displayExternalJs += '<h2>JavaScript file: ' + jsUrl + '</h2><pre>' + externalJsContent[jsUrl] + '</pre>';
                    }

                    var displayContent = displayHtml + displayCss + displayJs + displayExternalCss + displayExternalJs;
                    $('#code-display').html(displayContent);
                }
            },
            error: function(xhr, textStatus, errorThrown) {
                // Hide pre-loader and enable button
                $('#generate-code-btn').prop('disabled', false);
                $('#generate-code-text').show();
                $('#generate-code-loader').hide();

                $('#code-display').html('<p>Error: ' + xhr.responseText + '</p>');
            }
        });
    });
});
