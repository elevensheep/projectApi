import React from 'react';

const styles = {
    wrapper: {
        width: "150px",
        height: "200px",
        borderRadius: "8px"
    },
    img: {
        width: "150px",
        height: "200px",
        borderRadius: "8px",
        objectFit : "contain"
    },
};

const Book = (props) => {
    return (
        <div style={styles.wrapper}>
            <img src={props.bookImg} alt={props.bookAlt} style={styles.img}/>
            <p dangerouslySetInnerHTML={{ __html: props.bookTitle }}></p>
        </div>
    );
};

export default Book;