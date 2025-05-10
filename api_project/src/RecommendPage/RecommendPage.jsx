import React from 'react';
import Icons from './Component/Icons';
import Economy from './image/economy.png';
import Politics from './image/politics.png';
import Society from './image/society.png';
import Sports from './image/sports.png';
import World from './image/world.png';

const styles = {
    wrapper: {
        display: "flex",
        flexDirection: "row",
        justifyContent: "space-between",
    },
};
const RecommendPage = () => {
    return (
        <div style={styles.wrapper}>
            <Icons link="/economy" icon={Economy} text="경제" />
            <Icons link="/politics" icon={Politics} text="정치" />
            <Icons link="/sports" icon={Sports} text="스포츠" />
            <Icons link="/society" icon={Society} text="경제" />
            <Icons link="/world" icon={World} text="세계" />
        </div>
    );
};

export default RecommendPage;