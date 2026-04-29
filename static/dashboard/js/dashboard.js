document.addEventListener("DOMContentLoaded", function () {

    const labels = JSON.parse(document.getElementById('labels-data').textContent);
    const orderData = JSON.parse(document.getElementById('orders-data').textContent);
    const revenueData = JSON.parse(document.getElementById('revenue-data').textContent);
    const pieLabels = JSON.parse(document.getElementById('pie-labels-data').textContent);
    const pieData = JSON.parse(document.getElementById('pie-data').textContent);

    console.log("Pie Labels:", pieLabels);
    console.log("Pie Data:", pieData);

    // 📈 Orders
    new Chart(document.getElementById('orderChart'), {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Orders',
                data: orderData,
                fill: true,
                tension: 0.4
            }]
        }
    });

    // 💰 Revenue
    new Chart(document.getElementById('revenueChart'), {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Revenue',
                data: revenueData
            }]
        }
    });

    // 🍕 Pie (FIXED)
    new Chart(document.getElementById('pieChart'), {
        type: 'pie',
        data: {
            labels: pieLabels,
            datasets: [{
                data: pieData
            }]
        }
    });

});