document.addEventListener("DOMContentLoaded", () => {
    const button = document.getElementById("checkoutBtn");

    button.addEventListener("click", async (event) => {
        event.preventDefault(); // Prevent default form behavior if any

        // Gather form data
        const formData = {
            first_name: document.getElementById("first_name").value,
            last_name: document.getElementById("last_name").value,
            credit_card_number: document.getElementById("credit_card_number").value,
            expiration_date: document.getElementById("expiration_date").value,
            ccv: document.getElementById("ccv").value,
            shipping_address: document.getElementById("shipping_address").value
        };

        console.log("Sending data:", formData);

        try {
            // Send data to the server using fetch
            const response = await fetch("/submit-payment", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(formData)
            });

            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }

            const result = await response.json();
            console.log("Server response:", result);
            alert("Payment submitted successfully!");
        } catch (error) {
            console.error("Submission failed:", error);
            alert("Failed to submit payment.");
        }
    });
});