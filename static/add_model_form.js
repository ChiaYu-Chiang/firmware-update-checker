document.addEventListener('DOMContentLoaded', function () {
    const brand = document.querySelector('#brand');
    const other_brand = document.querySelector('#other_brand');
    other_brand.style.display = 'none';
    brand.addEventListener('change', function () {
        if (brand.value === 'other') {
            other_brand.style.display = 'block';
            other_brand.querySelector('input').required = true;
        } else {
            other_brand.style.display = 'none';
        }
    });
});