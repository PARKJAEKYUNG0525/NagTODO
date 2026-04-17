import { Link } from "react-router-dom";

const Title = () => (
    <Link
        to="/"
        className="text-white font-bold text-xl flex-shrink-0"
        aria-label="홈으로 이동"
    >
        화이팅
    </Link>
);

export default Title;