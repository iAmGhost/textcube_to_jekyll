(function () {
    document.addEventListener('DOMContentLoaded', function() {
        initMoreless();
        initFootnote();
    });

    function initMoreless() {
        for (const morelessBlock of document.querySelectorAll('.ttml-moreless')) {
            const openButton = morelessBlock.querySelector('.ttml-moreless__openButton');
            const closeButton = morelessBlock.querySelector('.ttml-moreless__closeButton');
            const content = morelessBlock.querySelector('.ttml-moreless__content');

            function toggleOpened() {
                morelessBlock.classList.toggle('ttml-moreless--opened');
            }

            openButton.addEventListener('click', (e) => {
                e.preventDefault();
                toggleOpened();
            });

            closeButton.addEventListener('click', (e) => {
                e.preventDefault();
                toggleOpened();
            });
        }
    }

    function initFootnote() {
        const footnotesContainer = document.getElementById('ttml-footnote-container');

        if (!footnotesContainer) {
            return;
        }

        let i = 0;

        for (const footnote of document.querySelectorAll('.ttml-footnote')) {
            const footnoteContent = footnote.innerHTML;
            footnote.innerHTML = `<sup><a href="#ttml-footnote-ref-${i + 1}" id="ttml-footnote-ref-${i + 1}-link"">[${i + 1}]</a></sup>`;

            const footnoteTextElem = document.createElement('div');
            footnoteTextElem.id = `ttml-footnote-ref-${i + 1}`;
            footnoteTextElem.innerHTML = `<sup><a href="#ttml-footnote-ref-${i + 1}-link">[${i + 1}]</a></sup> ${footnoteContent}`;
            footnotesContainer.appendChild(footnoteTextElem);

            i += 1;
        }

        if (i > 0) {
            footnotesContainer.classList.add('active');
        } else {
            footnotesContainer.classList.remove('active');
        }
    }
})();