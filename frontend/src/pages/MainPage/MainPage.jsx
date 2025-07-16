import React from 'react';
import Banner from './Component/banner.jsx'
import MainBookList from './Component/MainBookList.jsx';


const styles = {
    wrapper: {
        gap: "20px",
        display: "flex",
        flexDirection: "column",
    },
};

const MainPage = () => {
    return (
        <div style={styles.wrapper}>
            <Banner />
            <MainBookList />
        </div>
    );
};

export default MainPage;