const scrollAmount = 900;

document.querySelectorAll('.product-list').forEach(wrapper => {
    const container = wrapper.querySelector('.product-list__list');
    const leftButton = wrapper.querySelector('.arrow-left');
    const rightButton = wrapper.querySelector('.arrow-right');

    leftButton.addEventListener('click', () => {
        container.scrollBy({left: -scrollAmount, behavior: 'smooth'});
    });

    rightButton.addEventListener('click', () => {
        container.scrollBy({left: scrollAmount, behavior: 'smooth'});
    });
});

const content = document.querySelector('.content');
if (content) {
    const dataButton = content.querySelector('.button-section-data');
    const favoriteButton = content.querySelector('.button-section-favorite');
    const boughtButton = content.querySelector('.button-section-bought');

    const containerData = content.querySelector('.profile-data__section-data');
    const containerFavorite = content.querySelector('.profile-data__section-favorite');
    const containerbought = content.querySelector('.profile-data__section-bought');

    dataButton.addEventListener('click', () => {
        dataButton.classList.add('selected');
        favoriteButton.classList.remove('selected');
        boughtButton.classList.remove('selected');

        containerData.classList.remove('hidden');
        containerFavorite.classList.add('hidden');
        containerbought.classList.add('hidden');
    });
    favoriteButton.addEventListener('click', () => {
        dataButton.classList.remove('selected');
        favoriteButton.classList.add('selected');
        boughtButton.classList.remove('selected');

        containerData.classList.add('hidden');
        containerFavorite.classList.remove('hidden');
        containerbought.classList.add('hidden');
    });
    boughtButton.addEventListener('click', () => {
        dataButton.classList.remove('selected');
        favoriteButton.classList.remove('selected');
        boughtButton.classList.add('selected');
        
        containerData.classList.add('hidden');
        containerFavorite.classList.add('hidden');
        containerbought.classList.remove('hidden');
    });
}