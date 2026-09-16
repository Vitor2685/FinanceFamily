document.addEventListener("DOMContentLoaded", () => {

    const modal = document.getElementById("expenseModal");

    const openExpense = document.getElementById("openExpense");
    const openExpenseEmpty = document.getElementById("openExpenseEmpty");

    const closeExpense = document.getElementById("closeExpense");
    const cancelExpense = document.getElementById("cancelExpense");

    const toggleBalance = document.getElementById("toggleBalance");
    const balanceValue = document.getElementById("balanceValue");

    const mobileMenu = document.getElementById("mobileMenu");
    const sidebar = document.querySelector(".sidebar");


    /* =====================================================
       MODAL
    ===================================================== */

    function openModal() {

        if (!modal) return;

        modal.classList.add("show");

        document.body.style.overflow = "hidden";

        setTimeout(() => {

            const descricao = document.getElementById("descricao");

            if (descricao) {
                descricao.focus();
            }

        }, 200);
    }


    function closeModal() {

        if (!modal) return;

        modal.classList.remove("show");

        document.body.style.overflow = "";
    }


    if (openExpense) {
        openExpense.addEventListener("click", openModal);
    }


    if (openExpenseEmpty) {
        openExpenseEmpty.addEventListener("click", openModal);
    }


    if (closeExpense) {
        closeExpense.addEventListener("click", closeModal);
    }


    if (cancelExpense) {
        cancelExpense.addEventListener("click", closeModal);
    }


    if (modal) {

        modal.addEventListener("click", (event) => {

            if (event.target === modal) {
                closeModal();
            }

        });

    }


    document.addEventListener("keydown", (event) => {

        if (event.key === "Escape") {
            closeModal();
        }

    });


    /* =====================================================
       OCULTAR VALOR
    ===================================================== */

    let balanceHidden = false;

    const originalBalance =
        balanceValue
            ? balanceValue.textContent
            : "";


    if (toggleBalance && balanceValue) {

        toggleBalance.addEventListener("click", () => {

            balanceHidden = !balanceHidden;

            if (balanceHidden) {

                balanceValue.textContent = "R$ ••••••";

                toggleBalance.innerHTML =
                    '<i class="fa-regular fa-eye-slash"></i>';

            } else {

                balanceValue.textContent =
                    originalBalance;

                toggleBalance.innerHTML =
                    '<i class="fa-regular fa-eye"></i>';
            }

        });

    }


    /* =====================================================
       MOBILE MENU
    ===================================================== */

    if (mobileMenu && sidebar) {

        mobileMenu.addEventListener("click", () => {

            sidebar.classList.toggle("mobile-open");

        });


        document.querySelectorAll(".nav-item").forEach(item => {

            item.addEventListener("click", () => {

                if (window.innerWidth <= 900) {

                    sidebar.classList.remove("mobile-open");

                }

            });

        });

    }


    /* =====================================================
       MÁSCARA DE VALOR
    ===================================================== */

    const valorInput =
        document.getElementById("valor");


    if (valorInput) {

        valorInput.addEventListener("input", function () {

            let value =
                this.value.replace(/\D/g, "");


            if (!value) {

                this.value = "";

                return;
            }


            value =
                (parseInt(value, 10) / 100)
                .toFixed(2);


            value =
                value.replace(".", ",");


            this.value = value;

        });

    }


    /* =====================================================
       ANIMAÇÃO DOS CARDS
    ===================================================== */

    const cards =
        document.querySelectorAll(
            ".stat-card, .dashboard-card"
        );


    const observer =
        new IntersectionObserver(
            (entries) => {

                entries.forEach(entry => {

                    if (entry.isIntersecting) {

                        entry.target.style.opacity = "1";

                        entry.target.style.transform =
                            "translateY(0)";

                    }

                });

            },
            {
                threshold: 0.08
            }
        );


    cards.forEach(card => {

        card.style.opacity = "0";

        card.style.transform =
            "translateY(10px)";

        card.style.transition =
            "opacity .5s ease, transform .5s ease";

        observer.observe(card);

    });

});