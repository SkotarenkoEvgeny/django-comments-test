import { useEffect, useRef, useState } from "react";
import "./App.css";

const API_URL = import.meta.env.VITE_API_URL || "";
const WS_PROTOCOL =
    window.location.protocol === "https:"
        ? "wss:"
        : "ws:";

const WS_URL =
    `${WS_PROTOCOL}//${window.location.host}/ws/comments/`;

const PAGE_SIZE = 10;



function addReplyToTree(comments, newComment) {
    return comments.map((comment) => {
        if (comment.id === newComment.parent) {
            return {
                ...comment,
                replies: [
                    ...(comment.replies || []),
                    newComment,
                ],
            };
        }

        return {
            ...comment,
            replies: addReplyToTree(
                comment.replies || [],
                newComment
            ),
        };
    });
}


function getAvatarClass(userName = "") {
    const classes = [
        "avatar--blue",
        "avatar--purple",
        "avatar--green",
        "avatar--orange",
        "avatar--pink",
    ];

    const sum = userName
        .split("")
        .reduce(
            (total, char) =>
                total + char.charCodeAt(0),
            0
        );

    return classes[
        sum % classes.length
    ];
}


function formatDate(dateString) {
    return new Date(
        dateString
    ).toLocaleString(
        "ru-RU",
        {
            day: "2-digit",
            month: "2-digit",
            year: "2-digit",
            hour: "2-digit",
            minute: "2-digit",
        }
    );
}


function CommentItem({
    comment,
    onReply,
    level = 0,
}) {

    const avatarLetter =
        comment.user_name
            ?.charAt(0)
            .toUpperCase() || "?";

    const avatarClass =
        getAvatarClass(
            comment.user_name
        );


    return (

        <div
            className={
                level === 0
                    ? "comment comment--root"
                    : "comment comment--nested"
            }
        >

            {/* ==============================
                HEADER
            ============================== */}

            <div className="comment-header">

                <div className="comment-author">


                    {/* AVATAR */}

                    <div
                        className={
                            `avatar ${avatarClass}`
                        }
                    >
                        {avatarLetter}
                    </div>


                    {/* USER NAME */}

                    <strong className="author-name">

                        {comment.user_name}

                    </strong>


                    {/* DATE */}

                    <span className="comment-date">

                        {formatDate(
                            comment.created_at
                        )}

                    </span>


                    {/* ICONS */}

                    <div className="header-icons">

                        <span>
                            #
                        </span>

                        <span>
                            ♧
                        </span>

                        <button
                            type="button"

                            title="Reply"

                            onClick={() =>
                                onReply(
                                    comment.id,
                                    comment.user_name
                                )
                            }
                        >
                            ↩
                        </button>

                        <span>
                            ⓘ
                        </span>

                    </div>

                </div>


                {/* temp rating */}

                <div className="comment-rating">

                    <span>
                        ↑
                    </span>

                    <span className="rating-number">
                        0
                    </span>

                    <span>
                        ↓
                    </span>

                </div>

            </div>


            {/* ==============================
                COMMENT BODY
            ============================== */}

            <div className="comment-body">


                {/* HOME PAGE */}

                {comment.home_page && (

                    <a
                        className="comment-homepage"

                        href={
                            comment.home_page
                        }

                        target="_blank"

                        rel="noopener noreferrer"
                    >

                        {comment.home_page}

                    </a>

                )}


                {/* TEXT */}

                <div className="comment-text">

                    {comment.text}

                </div>


                {/* IMAGE */}

                {comment.image && (

                    <div className="comment-attachment">

                        <img
                            src={
                                comment.image
                            }

                            alt="Attachment"
                        />

                    </div>

                )}


                {/* TXT FILE */}

                {comment.text_file && (

                    <div className="comment-file">

                        <span>
                            ▤
                        </span>

                        <a
                            href={
                                comment.text_file
                            }

                            target="_blank"

                            rel="noopener noreferrer"
                        >

                            Open TXT file

                        </a>

                    </div>

                )}


                {/* REPLY BUTTON */}

                <button
                    type="button"

                    className="text-reply-button"

                    onClick={() =>
                        onReply(
                            comment.id,
                            comment.user_name
                        )
                    }
                >

                    Reply

                </button>

            </div>


            {/* ==============================
                REPLIES
            ============================== */}

            {comment.replies?.length > 0 && (

                <div className="replies">

                    {comment.replies.map(
                        (reply) => (

                            <CommentItem

                                key={
                                    reply.id
                                }

                                comment={
                                    reply
                                }

                                onReply={
                                    onReply
                                }

                                level={
                                    level + 1
                                }

                            />

                        )
                    )}

                </div>

            )}

        </div>

    );
}


// ======================================================
// APP
// ======================================================

function App() {


    // ==================================================
    // COMMENTS
    // ==================================================

    const [comments, setComments] =
        useState([]);


    // ==================================================
    // ERROR
    // ==================================================

    const [error, setError] =
        useState("");


    // ==================================================
    // CAPTCHA
    // ==================================================

    const [captcha, setCaptcha] =
        useState(null);


    // ==================================================
    // FILES
    // ==================================================

    const [image, setImage] =
        useState(null);

    const [textFile, setTextFile] =
        useState(null);


    // ==================================================
    // REPLY
    // ==================================================

    const [replyToUser, setReplyToUser] =
        useState(null);


    // ==================================================
    // SORTING
    // ==================================================

    const [ordering, setOrdering] =
        useState("-created_at");


    // ==================================================
    // PAGINATION
    // ==================================================

    const [page, setPage] =
        useState(1);

    const [totalCount, setTotalCount] =
        useState(0);


    // ==================================================
    // REFS
    // ==================================================

    const formRef =
        useRef(null);

    const imageInputRef =
        useRef(null);

    const textFileInputRef =
        useRef(null);


    // Актуальные значения для WebSocket

    const pageRef =
        useRef(1);

    const orderingRef =
        useRef("-created_at");


    // ==================================================
    // FORM
    // ==================================================

    const [form, setForm] =
        useState({

            user_name: "",

            email: "",

            home_page: "",

            text: "",

            captcha_id: "",

            captcha_value: "",

            parent: null,

        });


    useEffect(() => {

        pageRef.current =
            page;

    }, [page]);


    useEffect(() => {

        orderingRef.current =
            ordering;

    }, [ordering]);


    // ==================================================
    // TOTAL PAGES
    // ==================================================

    const totalPages =
        Math.max(
            1,
            Math.ceil(
                totalCount /
                PAGE_SIZE
            )
        );


    // ==================================================
    // LOAD COMMENTS
    // ==================================================

    const loadComments =
        async (
            currentOrdering = orderingRef.current,
            currentPage = pageRef.current
        ) => {

            try {

                const response =
                    await fetch(

                        `${API_URL}/api/comments/?ordering=${currentOrdering}&page=${currentPage}`

                    );


                if (!response.ok) {

                    throw new Error(
                        "Failed to load comments"
                    );

                }


                const data =
                    await response.json();


                // DRF pagination

                if (
                    Array.isArray(
                        data.results
                    )
                ) {

                    setComments(
                        data.results
                    );

                    setTotalCount(
                        data.count || 0
                    );

                }


                // Если pagination отключена

                else {

                    setComments(
                        data
                    );

                    setTotalCount(
                        data.length
                    );

                }


            } catch (error) {

                console.error(
                    error
                );


                setError(
                    "Failed to load comments"
                );

            }

        };


    // ==================================================
    // LOAD CAPTCHA
    // ==================================================

    const loadCaptcha =
        async () => {

            try {

                const response =
                    await fetch(

                        `${API_URL}/api/captcha/`

                    );


                if (!response.ok) {

                    throw new Error(
                        "Failed to load CAPTCHA"
                    );

                }


                const data =
                    await response.json();


                setCaptcha(
                    data
                );


                setForm(
                    (
                        currentForm
                    ) => ({

                        ...currentForm,

                        captcha_id:
                            data.captcha_id,

                        captcha_value:
                            "",

                    })
                );


            } catch (error) {

                console.error(
                    error
                );


                setError(
                    "Failed to load CAPTCHA"
                );

            }

        };


    // ==================================================
    // INITIAL LOAD + WEBSOCKET
    // ==================================================

    useEffect(() => {


        // Загружаем первую страницу

        loadComments(
            "-created_at",
            1
        );


        // Загружаем CAPTCHA

        loadCaptcha();


        // ==================================================
        // CREATE WEBSOCKET
        // ==================================================

        const socket =
            new WebSocket(
                WS_URL
            );


        // ==================================================
        // WS OPEN
        // ==================================================

        socket.onopen =
            () => {

                console.log(
                    "WebSocket connected"
                );

            };


        // ==================================================
        // WS MESSAGE
        // ==================================================

        socket.onmessage =
            (event) => {


                const data =
                    JSON.parse(
                        event.data
                    );


                if (
                    data.type !==
                    "comment_created"
                ) {

                    return;

                }


                const newComment =
                    data.comment;


                if (
                    !newComment.parent
                ) {


                    loadComments(

                        orderingRef.current,

                        pageRef.current

                    );


                    return;

                }


                // ==========================================
                // НОВЫЙ REPLY
                // ==========================================

                setComments(
                    (
                        currentComments
                    ) =>

                        addReplyToTree(

                            currentComments,

                            newComment

                        )
                );

            };


        // ==================================================
        // WS ERROR
        // ==================================================

        socket.onerror =
            (error) => {

                console.error(

                    "WebSocket error:",

                    error

                );

            };


        // ==================================================
        // WS CLOSE
        // ==================================================

        socket.onclose =
            () => {

                console.log(
                    "WebSocket disconnected"
                );

            };


        // ==================================================
        // CLEANUP
        // ==================================================

        return () => {

            socket.close();

        };


    }, []);


    // ==================================================
    // SORT
    // ==================================================

    const handleSort =
        (field) => {

            let newOrdering;


            // ASC -> DESC

            if (
                ordering === field
            ) {

                newOrdering =
                    `-${field}`;

            }


            // DESC -> ASC

            else if (
                ordering ===
                `-${field}`
            ) {

                newOrdering =
                    field;

            }


            // Другое поле -> ASC

            else {

                newOrdering =
                    field;

            }


            // Обновляем state

            setOrdering(
                newOrdering
            );


            // Сразу обновляем ref

            orderingRef.current =
                newOrdering;


            // При новой сортировке
            // переходим на страницу 1

            setPage(
                1
            );


            pageRef.current =
                1;


            // Загружаем данные

            loadComments(
                newOrdering,
                1
            );

        };


    // ==================================================
    // SORT ICON
    // ==================================================

    const getSortIcon =
        (field) => {

            if (
                ordering === field
            ) {

                return "↑";

            }


            if (
                ordering ===
                `-${field}`
            ) {

                return "↓";

            }


            return "";

        };


    // ==================================================
    // CHANGE PAGE
    // ==================================================

    const handlePageChange =
        (newPage) => {


            if (
                newPage < 1 ||
                newPage > totalPages
            ) {

                return;

            }


            // State

            setPage(
                newPage
            );


            // Ref

            pageRef.current =
                newPage;


            // Загружаем страницу

            loadComments(

                orderingRef.current,

                newPage

            );


            // Скролл вверх

            window.scrollTo({

                top: 0,

                behavior:
                    "smooth",

            });

        };


    // ==================================================
    // FORM CHANGE
    // ==================================================

    const handleChange =
        (event) => {

            const {
                name,
                value,
            } = event.target;


            setForm(
                (
                    currentForm
                ) => ({

                    ...currentForm,

                    [name]:
                        value,

                })
            );

        };


    // ==================================================
    // REPLY
    // ==================================================

    const handleReply =
        (
            commentId,
            userName
        ) => {


            setForm(
                (
                    currentForm
                ) => ({

                    ...currentForm,

                    parent:
                        commentId,

                })
            );


            setReplyToUser(
                userName
            );


            // Скроллим к форме

            formRef.current
                ?.scrollIntoView({

                    behavior:
                        "smooth",

                    block:
                        "start",

                });

        };


    // ==================================================
    // CANCEL REPLY
    // ==================================================

    const cancelReply =
        () => {


            setForm(
                (
                    currentForm
                ) => ({

                    ...currentForm,

                    parent:
                        null,

                })
            );


            setReplyToUser(
                null
            );

        };


    // ==================================================
    // SUBMIT
    // ==================================================

    const handleSubmit =
        async (event) => {


            event.preventDefault();


            setError("");


            const formData =
                new FormData();


            // ==================================================
            // USER NAME
            // ==================================================

            formData.append(

                "user_name",

                form.user_name

            );


            // ==================================================
            // EMAIL
            // ==================================================

            formData.append(

                "email",

                form.email

            );


            // ==================================================
            // HOME PAGE
            // ==================================================

            if (
                form.home_page
            ) {

                formData.append(

                    "home_page",

                    form.home_page

                );

            }


            // ==================================================
            // TEXT
            // ==================================================

            formData.append(

                "text",

                form.text

            );


            // ==================================================
            // PARENT
            // ==================================================

            if (
                form.parent
            ) {

                formData.append(

                    "parent",

                    form.parent

                );

            }


            // ==================================================
            // CAPTCHA
            // ==================================================

            formData.append(

                "captcha_id",

                form.captcha_id

            );


            formData.append(

                "captcha_value",

                form.captcha_value

            );


            // ==================================================
            // IMAGE
            // ==================================================

            if (image) {

                formData.append(

                    "image",

                    image

                );

            }


            // ==================================================
            // TXT
            // ==================================================

            if (textFile) {

                formData.append(

                    "text_file",

                    textFile

                );

            }


            // ==================================================
            // SEND
            // ==================================================

            try {

                const response =
                    await fetch(

                        `${API_URL}/api/comments/`,

                        {

                            method:
                                "POST",

                            body:
                                formData,

                        }

                    );


                const data =
                    await response.json();


                // ==================================================
                // API ERROR
                // ==================================================

                if (
                    !response.ok
                ) {


                    setError(

                        JSON.stringify(
                            data
                        )

                    );


                    // CAPTCHA одноразовая,
                    // поэтому загружаем новую

                    await loadCaptcha();


                    return;

                }


                // ==================================================
                // SUCCESS
                // ==================================================


                // Очищаем форму

                setForm({

                    user_name:
                        "",

                    email:
                        "",

                    home_page:
                        "",

                    text:
                        "",

                    captcha_id:
                        "",

                    captcha_value:
                        "",

                    parent:
                        null,

                });


                // Убираем Reply

                setReplyToUser(
                    null
                );


                // Убираем image

                setImage(
                    null
                );


                // Убираем TXT

                setTextFile(
                    null
                );


                // Очищаем input image

                if (
                    imageInputRef.current
                ) {

                    imageInputRef
                        .current
                        .value = "";

                }


                // Очищаем input TXT

                if (
                    textFileInputRef.current
                ) {

                    textFileInputRef
                        .current
                        .value = "";

                }


                // Загружаем новую CAPTCHA

                await loadCaptcha();


                // Сам комментарий вручную
                // НЕ добавляем.
                //
                // Он придёт через WebSocket.


            } catch (error) {

                console.error(
                    error
                );


                setError(
                    "Failed to create comment"
                );

            }

        };


    // ==================================================
    // JSX
    // ==================================================

    return (

        <div className="app">

            <main className="container">


                {/* ==========================
                    TITLE
                ========================== */}

                <h1 className="page-title">

                    Comments

                </h1>


                {/* ==========================
                    SORTING
                ========================== */}

                <div className="sorting-bar">


                    <span className="sorting-label">

                        Sort by:

                    </span>


                    {/* USER NAME */}

                    <button
                        type="button"

                        className={
                            ordering.includes(
                                "user_name"
                            )
                                ? "sort-button active"
                                : "sort-button"
                        }

                        onClick={() =>
                            handleSort(
                                "user_name"
                            )
                        }
                    >

                        User Name

                        <span>

                            {getSortIcon(
                                "user_name"
                            )}

                        </span>

                    </button>


                    {/* EMAIL */}

                    <button
                        type="button"

                        className={
                            ordering.includes(
                                "email"
                            )
                                ? "sort-button active"
                                : "sort-button"
                        }

                        onClick={() =>
                            handleSort(
                                "email"
                            )
                        }
                    >

                        E-mail

                        <span>

                            {getSortIcon(
                                "email"
                            )}

                        </span>

                    </button>


                    {/* DATE */}

                    <button
                        type="button"

                        className={
                            ordering.includes(
                                "created_at"
                            )
                                ? "sort-button active"
                                : "sort-button"
                        }

                        onClick={() =>
                            handleSort(
                                "created_at"
                            )
                        }
                    >

                        Date

                        <span>

                            {getSortIcon(
                                "created_at"
                            )}

                        </span>

                    </button>

                </div>


                {/* ==========================
                    COMMENTS
                ========================== */}

                <section className="comments-panel">


                    {comments.length === 0
                        && !error && (

                        <div>

                            No comments yet.

                        </div>

                    )}


                    {comments.map(
                        (comment) => (

                            <CommentItem

                                key={
                                    comment.id
                                }

                                comment={
                                    comment
                                }

                                onReply={
                                    handleReply
                                }

                            />

                        )
                    )}

                </section>


                {/* ==========================
                    PAGINATION
                ========================== */}

                {totalPages > 1 && (

                    <div className="pagination">


                        {/* PREVIOUS */}

                        <button

                            type="button"

                            className="pagination-button"

                            disabled={
                                page === 1
                            }

                            onClick={() =>
                                handlePageChange(
                                    page - 1
                                )
                            }

                        >

                            ← Previous

                        </button>


                        {/* PAGE NUMBERS */}

                        <div className="pagination-pages">

                            {Array
                                .from(
                                    {
                                        length:
                                            totalPages
                                    },
                                    (
                                        _,
                                        index
                                    ) =>
                                        index + 1
                                )
                                .map(
                                    (
                                        pageNumber
                                    ) => (

                                        <button

                                            key={
                                                pageNumber
                                            }

                                            type="button"

                                            className={
                                                page ===
                                                pageNumber

                                                    ? "pagination-number active"

                                                    : "pagination-number"
                                            }

                                            onClick={() =>
                                                handlePageChange(
                                                    pageNumber
                                                )
                                            }

                                        >

                                            {pageNumber}

                                        </button>

                                    )
                                )}

                        </div>


                        {/* NEXT */}

                        <button

                            type="button"

                            className="pagination-button"

                            disabled={
                                page ===
                                totalPages
                            }

                            onClick={() =>
                                handlePageChange(
                                    page + 1
                                )
                            }

                        >

                            Next →

                        </button>

                    </div>

                )}


                {/* ==========================
                    FORM
                ========================== */}

                <section
                    className="form-panel"

                    ref={
                        formRef
                    }
                >


                    <h2>

                        Add comment

                    </h2>


                    {/* ==========================
                        REPLY NOTICE
                    ========================== */}

                    {form.parent && (

                        <div className="reply-notice">


                            <span>

                                Replying to{" "}

                                <strong>

                                    {replyToUser}

                                </strong>

                            </span>


                            <button

                                type="button"

                                onClick={
                                    cancelReply
                                }

                            >

                                ×

                            </button>

                        </div>

                    )}


                    {/* ==========================
                        FORM
                    ========================== */}

                    <form
                        onSubmit={
                            handleSubmit
                        }
                    >


                        {/* USER DATA */}

                        <div className="form-grid">


                            <input

                                type="text"

                                name="user_name"

                                placeholder="User Name"

                                value={
                                    form.user_name
                                }

                                onChange={
                                    handleChange
                                }

                                required

                            />


                            <input

                                type="email"

                                name="email"

                                placeholder="E-mail"

                                value={
                                    form.email
                                }

                                onChange={
                                    handleChange
                                }

                                required

                            />


                            <input

                                type="url"

                                name="home_page"

                                placeholder="Home page"

                                value={
                                    form.home_page
                                }

                                onChange={
                                    handleChange
                                }

                            />

                        </div>


                        {/* ==========================
                            TEXT
                        ========================== */}

                        <textarea

                            name="text"

                            placeholder="Your comment..."

                            value={
                                form.text
                            }

                            onChange={
                                handleChange
                            }

                            required

                        />


                        {/* ==========================
                            FILES
                        ========================== */}

                        <div className="file-row">


                            {/* IMAGE */}

                            <label>

                                📷 Add image

                                <input

                                    ref={
                                        imageInputRef
                                    }

                                    type="file"

                                    accept=".jpg,.jpeg,.png,.gif"

                                    onChange={
                                        (event) =>

                                            setImage(

                                                event
                                                    .target
                                                    .files[0]

                                                || null

                                            )
                                    }

                                />

                            </label>


                            {/* TXT */}

                            <label>

                                📄 Add TXT

                                <input

                                    ref={
                                        textFileInputRef
                                    }

                                    type="file"

                                    accept=".txt,text/plain"

                                    onChange={
                                        (event) =>

                                            setTextFile(

                                                event
                                                    .target
                                                    .files[0]

                                                || null

                                            )
                                    }

                                />

                            </label>


                            {/* SELECTED IMAGE */}

                            {image && (

                                <span>

                                    {image.name}

                                </span>

                            )}


                            {/* SELECTED TXT */}

                            {textFile && (

                                <span>

                                    {textFile.name}

                                </span>

                            )}

                        </div>


                        {/* ==========================
                            FOOTER
                        ========================== */}

                        <div className="form-footer">


                            {/* CAPTCHA */}

                            <div className="captcha">


                                {captcha && (

                                    <img

                                        src={
                                            captcha.image
                                        }

                                        alt="CAPTCHA"

                                    />

                                )}


                                <input

                                    type="text"

                                    name="captcha_value"

                                    placeholder="Code"

                                    value={
                                        form.captcha_value
                                    }

                                    onChange={
                                        handleChange
                                    }

                                    required

                                />


                                <button

                                    type="button"

                                    title="Refresh CAPTCHA"

                                    onClick={
                                        loadCaptcha
                                    }

                                >

                                    ↻

                                </button>

                            </div>


                            {/* SEND */}

                            <button

                                className="submit-button"

                                type="submit"

                            >

                                Send

                            </button>

                        </div>


                        {/* ==========================
                            ERROR
                        ========================== */}

                        {error && (

                            <div className="error">

                                {error}

                            </div>

                        )}

                    </form>

                </section>

            </main>

        </div>

    );
}


export default App;
