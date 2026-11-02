document.addEventListener("DOMContentLoaded", () => {

    const copyButton = document.getElementById("copyInstall");

    if (copyButton) {

        copyButton.addEventListener("click", async () => {

            const command = "pip install dezh";

            try {

                await navigator.clipboard.writeText(command);

                const originalText = copyButton.textContent;

                copyButton.textContent = "Copied";

                setTimeout(() => {
                    copyButton.textContent = originalText;
                }, 1500);

            } catch (error) {

                console.error(
                    "Failed to copy command:",
                    error
                );

            }

        });

    }


    /*
     * Reveal sections when they enter
     * the viewport.
     */

    const revealElements = document.querySelectorAll(
        ".feature-card, .architecture-node, .code-window"
    );


    const observer = new IntersectionObserver(
        (entries) => {

            entries.forEach((entry) => {

                if (entry.isIntersecting) {

                    entry.target.classList.add(
                        "is-visible"
                    );

                    observer.unobserve(
                        entry.target
                    );

                }

            });

        },
        {
            threshold: 0.12
        }
    );


    revealElements.forEach((element) => {
        observer.observe(element);
    });


    /*
     * Prevent default behavior for
     * placeholder links.
     */

    document.querySelectorAll('a[href="#"]').forEach((link) => {

        link.addEventListener("click", (event) => {
            event.preventDefault();
        });

    });

});