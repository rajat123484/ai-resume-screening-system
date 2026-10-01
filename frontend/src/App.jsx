import React, { Fragment, useState } from "react";
import "./App.css";

function App() {
    const [jobDescription, setJobDescription] = useState("");
    const [resumes, setResumes] = useState([]);
    const [results, setResults] = useState(null);

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const [expandedCandidate, setExpandedCandidate] = useState(null);

    const [searchTerm, setSearchTerm] = useState("");
    const [decisionFilter, setDecisionFilter] = useState("ALL");
    const [sortBy, setSortBy] = useState("rank");

    // =========================================================
    // FILE UPLOAD
    // =========================================================

    const handleFileChange = (event) => {
        const selectedFiles = Array.from(event.target.files);

        const validFiles = selectedFiles.filter((file) => {
            const name = file.name.toLowerCase();

            return (
                name.endsWith(".pdf") ||
                name.endsWith(".docx")
            );
        });

        if (validFiles.length !== selectedFiles.length) {
            setError(
                "Only PDF and DOCX resume files are supported."
            );
        } else {
            setError("");
        }

        setResumes((previousFiles) => {
            const existingKeys = new Set(
                previousFiles.map(
                    (file) =>
                        `${file.name}-${file.size}-${file.lastModified}`
                )
            );

            const newFiles = [];

            validFiles.forEach((file) => {
                const fileKey =
                    `${file.name}-${file.size}-${file.lastModified}`;

                if (
                    !existingKeys.has(fileKey) &&
                    !newFiles.some(
                        (existingFile) =>
                            `${existingFile.name}-${existingFile.size}-${existingFile.lastModified}` ===
                            fileKey
                    )
                ) {
                    newFiles.push(file);
                }
            });

            return [
                ...previousFiles,
                ...newFiles
            ];
        });

        setResults(null);

        event.target.value = "";
    };

    // =========================================================
    // REMOVE RESUME
    // =========================================================

    const removeResume = (index) => {
        setResumes((previous) =>
            previous.filter(
                (_, i) => i !== index
            )
        );

        setResults(null);
    };

    // =========================================================
    // SCREEN CANDIDATES
    // =========================================================

    const screenCandidates = async () => {
        setError("");
        setResults(null);

        if (!jobDescription.trim()) {
            setError(
                "Please enter a job description."
            );
            return;
        }

        if (resumes.length === 0) {
            setError(
                "Please upload at least one PDF or DOCX resume."
            );
            return;
        }

        const formData = new FormData();

        formData.append(
            "job_description",
            jobDescription
        );

        resumes.forEach((resume) => {
            formData.append(
                "resumes",
                resume
            );
        });

        try {
            setLoading(true);

            const response = await fetch(
                "https://ai-resume-screening-system-0adi.onrender.com/screen-candidates",
                {
                    method: "POST",
                    body: formData,
                }
            );

            if (!response.ok) {
                throw new Error(
                    `Server error: ${response.status}`
                );
            }

            const data = await response.json();

            if (data.error) {
                throw new Error(data.error);
            }

            setResults(data);

        } catch (err) {
            setError(
                err.message ||
                "Something went wrong while screening candidates."
            );

        } finally {
            setLoading(false);
        }
    };

    // =========================================================
    // EXPAND / COLLAPSE CANDIDATE
    // =========================================================

    const toggleCandidate = (index) => {
        setExpandedCandidate(
            expandedCandidate === index
                ? null
                : index
        );
    };

    // =========================================================
    // FILE TYPE
    // =========================================================

    const getFileType = (filename) => {
        if (
            filename
                .toLowerCase()
                .endsWith(".docx")
        ) {
            return "DOCX";
        }

        return "PDF";
    };

    // =========================================================
    // DECISION CLASS
    // =========================================================

    const getDecisionClass = (decision) => {
        if (decision === "SHORTLIST") {
            return "decision-shortlist";
        }

        if (decision === "REVIEW") {
            return "decision-review";
        }

        return "decision-reject";
    };

    // =========================================================
    // SEARCH + FILTER + SORT
    // =========================================================

    const filteredCandidates =
        results?.candidates
            ?.filter((candidate) => {

                const matchesSearch =
                    candidate.filename
                        .toLowerCase()
                        .includes(
                            searchTerm.toLowerCase()
                        );

                const matchesDecision =
                    decisionFilter === "ALL" ||
                    candidate.decision ===
                        decisionFilter;

                return (
                    matchesSearch &&
                    matchesDecision
                );
            })
            ?.sort((a, b) => {

                if (sortBy === "final") {
                    return (
                        b.final_score -
                        a.final_score
                    );
                }

                if (sortBy === "ats") {
                    return (
                        b.ats_score -
                        a.ats_score
                    );
                }

                if (sortBy === "jd") {
                    return (
                        b.jd_match_score -
                        a.jd_match_score
                    );
                }

                return (
                    a.rank -
                    b.rank
                );
            }) || [];

    return (
        <div className="app">

            {/* =================================================
                HEADER
            ================================================= */}

            <header className="top-header">

                <div>

                    <h1>
                        AI Resume Screening System
                    </h1>

                    <p>
                        AI-Based Resume Screening and
                        Candidate Shortlisting System
                    </p>

                </div>

            </header>


            {/* =================================================
                MAIN CONTAINER
            ================================================= */}

            <main className="main-container">


                {/* =================================================
                    JOB DESCRIPTION
                ================================================= */}

                <section className="card">

                    <div className="section-header">

                        <div>

                            <h2>
                                Job Description
                            </h2>

                            <p>
                                Enter the job requirements
                                for candidate matching.
                            </p>

                        </div>

                    </div>


                    <textarea
                        className="job-description"
                        value={jobDescription}
                        onChange={(event) =>
                            setJobDescription(
                                event.target.value
                            )
                        }
                        placeholder="Enter job description here..."
                    />

                </section>


                {/* =================================================
                    RESUME UPLOAD
                ================================================= */}

                <section className="card">

                    <div className="section-header">

                        <div>

                            <h2>
                                Upload Resumes
                            </h2>

                            <p>
                                Upload multiple PDF or
                                DOCX resumes.
                            </p>

                        </div>

                    </div>


                    <label className="upload-box">

                        <input
                            type="file"
                            accept=".pdf,.docx"
                            multiple
                            onChange={
                                handleFileChange
                            }
                        />

                        <div className="upload-icon">
                            +
                        </div>

                        <h3>
                            Upload PDF or DOCX resumes
                        </h3>

                        <p>
                            Click to select multiple
                            resume files
                        </p>

                        <span className="upload-hint">
                            PDF and DOCX files only
                        </span>

                    </label>


                    {/* =================================================
                        SELECTED RESUMES
                    ================================================= */}

                    {resumes.length > 0 && (

                        <div className="uploaded-files">

                            <div className="uploaded-header">

                                <strong>
                                    Selected Resumes
                                </strong>

                                <span>
                                    {resumes.length} file
                                    {resumes.length !== 1
                                        ? "s"
                                        : ""}
                                </span>

                            </div>


                            {resumes.map(
                                (resume, index) => (

                                    <div
                                        className="resume-file"
                                        key={`${resume.name}-${resume.size}-${resume.lastModified}`}
                                    >

                                        <div className="file-info">

                                            <div className="file-icon">

                                                {getFileType(
                                                    resume.name
                                                )}

                                            </div>


                                            <div>

                                                <div className="file-name">

                                                    {resume.name}

                                                </div>


                                                <div className="file-size">

                                                    {(
                                                        resume.size /
                                                        1024
                                                    ).toFixed(1)}{" "}
                                                    KB

                                                </div>

                                            </div>

                                        </div>


                                        <button
                                            type="button"
                                            className="remove-file"
                                            onClick={() =>
                                                removeResume(
                                                    index
                                                )
                                            }
                                        >
                                            ×
                                        </button>

                                    </div>

                                )
                            )}

                        </div>

                    )}

                </section>


                {/* =================================================
                    ERROR
                ================================================= */}

                {error && (

                    <div className="error-message">

                        {error}

                    </div>

                )}


                {/* =================================================
                    SCREEN BUTTON
                ================================================= */}

                <button
                    className="screen-button"
                    onClick={screenCandidates}
                    disabled={loading}
                >

                    {loading
                        ? "Screening Candidates..."
                        : "Screen Candidates"}

                </button>


                {/* =================================================
                    RESULTS
                ================================================= */}

                {results && (

                    <section className="results-section">

                        <div className="results-header">

                            <div>

                                <h2>
                                    Screening Results
                                </h2>

                                <p>

                                    {results.total_candidates}{" "}
                                    candidate
                                    {results.total_candidates !==
                                    1
                                        ? "s"
                                        : ""}{" "}
                                    screened

                                </p>

                            </div>

                        </div>


                        {/* =================================================
                            SEARCH / FILTER / SORT
                        ================================================= */}

                        <div className="result-controls">

                            <input
                                type="text"
                                placeholder="Search candidate..."
                                value={searchTerm}
                                onChange={(event) =>
                                    setSearchTerm(
                                        event.target.value
                                    )
                                }
                            />


                            <select
                                value={decisionFilter}
                                onChange={(event) =>
                                    setDecisionFilter(
                                        event.target.value
                                    )
                                }
                            >

                                <option value="ALL">
                                    All Decisions
                                </option>

                                <option value="SHORTLIST">
                                    Shortlisted
                                </option>

                                <option value="REVIEW">
                                    Review
                                </option>

                                <option value="NOT SHORTLIST">
                                    Not Shortlisted
                                </option>

                            </select>


                            <select
                                value={sortBy}
                                onChange={(event) =>
                                    setSortBy(
                                        event.target.value
                                    )
                                }
                            >

                                <option value="rank">
                                    Sort by Rank
                                </option>

                                <option value="final">
                                    Sort by Final Score
                                </option>

                                <option value="ats">
                                    Sort by ATS Score
                                </option>

                                <option value="jd">
                                    Sort by JD Match
                                </option>

                            </select>

                        </div>


                        {/* =================================================
                            RESULT COUNT
                        ================================================= */}

                        <div className="filtered-count">

                            Showing{" "}

                            <strong>
                                {filteredCandidates.length}
                            </strong>{" "}

                            of{" "}

                            <strong>
                                {results.total_candidates}
                            </strong>{" "}

                            candidates

                        </div>


                        {/* =================================================
                            EMPTY RESULT
                        ================================================= */}

                        {filteredCandidates.length ===
                            0 && (

                            <div className="empty-results">

                                No candidates match the
                                current search/filter.

                            </div>

                        )}


                        {/* =================================================
                            RESULT TABLE
                        ================================================= */}

                        {filteredCandidates.length >
                            0 && (

                            <div className="table-wrapper">

                                <table className="results-table">

                                    <thead>

                                        <tr>

                                            <th>
                                                Rank
                                            </th>

                                            <th>
                                                Candidate
                                            </th>

                                            <th>
                                                ATS Score
                                            </th>

                                            <th>
                                                Semantic
                                            </th>

                                            <th>
                                                Skill Match
                                            </th>

                                            <th>
                                                JD Match
                                            </th>

                                            <th>
                                                Final Score
                                            </th>

                                            <th>
                                                Decision
                                            </th>

                                            <th>
                                                Details
                                            </th>

                                        </tr>

                                    </thead>


                                    <tbody>

                                        {filteredCandidates.map(
                                            (
                                                candidate,
                                                index
                                            ) => (

                                                <Fragment
                                                    key={`${candidate.filename}-${index}`}
                                                >

                                                    <tr>

                                                        <td>

                                                            <strong>
                                                                #
                                                                {
                                                                    candidate.rank
                                                                }
                                                            </strong>

                                                        </td>


                                                        <td>

                                                            <div className="candidate-name">

                                                                {
                                                                    candidate.filename
                                                                }

                                                            </div>

                                                        </td>


                                                        <td>

                                                            <span className="score-badge">

                                                                {
                                                                    candidate.ats_score
                                                                }

                                                            </span>

                                                        </td>


                                                        <td>

                                                            {
                                                                candidate.semantic_score
                                                            }

                                                        </td>


                                                        <td>

                                                            {
                                                                candidate.skill_match_score
                                                            }

                                                        </td>


                                                        <td>

                                                            {
                                                                candidate.jd_match_score
                                                            }

                                                        </td>


                                                        <td>

                                                            <strong className="final-score">

                                                                {
                                                                    candidate.final_score
                                                                }

                                                            </strong>

                                                        </td>


                                                        <td>

                                                            <span
                                                                className={`decision-badge ${getDecisionClass(
                                                                    candidate.decision
                                                                )}`}
                                                            >

                                                                {
                                                                    candidate.decision
                                                                }

                                                            </span>

                                                        </td>


                                                        <td>

                                                            <button
                                                                type="button"
                                                                className="details-button"
                                                                onClick={() =>
                                                                    toggleCandidate(
                                                                        index
                                                                    )
                                                                }
                                                            >

                                                                {expandedCandidate ===
                                                                index
                                                                    ? "Hide"
                                                                    : "View"}

                                                            </button>

                                                        </td>

                                                    </tr>


                                                    {/* =================================================
                                                        EXPANDED DETAILS
                                                    ================================================= */}

                                                    {expandedCandidate ===
                                                        index && (

                                                        <tr className="details-row">

                                                            <td
                                                                colSpan="9"
                                                            >

                                                                <div className="candidate-details">


                                                                    <div className="detail-block">

                                                                        <h4>
                                                                            Matching Skills
                                                                        </h4>

                                                                        <div className="skill-list">

                                                                            {candidate.matching_skills
                                                                                ?.length >
                                                                            0 ? (

                                                                                candidate.matching_skills.map(
                                                                                    (
                                                                                        skill,
                                                                                        skillIndex
                                                                                    ) => (

                                                                                        <span
                                                                                            className="skill-tag matching"
                                                                                            key={`${skill}-${skillIndex}`}
                                                                                        >

                                                                                            ✓{" "}
                                                                                            {
                                                                                                skill
                                                                                            }

                                                                                        </span>

                                                                                    )
                                                                                )

                                                                            ) : (

                                                                                <span>
                                                                                    No matching
                                                                                    skills
                                                                                    detected.
                                                                                </span>

                                                                            )}

                                                                        </div>

                                                                    </div>


                                                                    <div className="detail-block">

                                                                        <h4>
                                                                            Missing Skills
                                                                        </h4>

                                                                        <div className="skill-list">

                                                                            {candidate.missing_skills
                                                                                ?.length >
                                                                            0 ? (

                                                                                candidate.missing_skills.map(
                                                                                    (
                                                                                        skill,
                                                                                        skillIndex
                                                                                    ) => (

                                                                                        <span
                                                                                            className="skill-tag missing"
                                                                                            key={`${skill}-${skillIndex}`}
                                                                                        >

                                                                                            ✕{" "}
                                                                                            {
                                                                                                skill
                                                                                            }

                                                                                        </span>

                                                                                    )
                                                                                )

                                                                            ) : (

                                                                                <span>
                                                                                    No missing
                                                                                    skills
                                                                                    detected.
                                                                                </span>

                                                                            )}

                                                                        </div>

                                                                    </div>


                                                                    <div className="score-summary">

                                                                        <div>

                                                                            <span>
                                                                                ATS
                                                                                Compatibility
                                                                            </span>

                                                                            <strong>

                                                                                {
                                                                                    candidate.ats_score
                                                                                }

                                                                                /100

                                                                            </strong>

                                                                        </div>


                                                                        <div>

                                                                            <span>
                                                                                Semantic
                                                                                Match
                                                                            </span>

                                                                            <strong>

                                                                                {
                                                                                    candidate.semantic_score
                                                                                }

                                                                                /100

                                                                            </strong>

                                                                        </div>


                                                                        <div>

                                                                            <span>
                                                                                Skill
                                                                                Match
                                                                            </span>

                                                                            <strong>

                                                                                {
                                                                                    candidate.skill_match_score
                                                                                }

                                                                                /100

                                                                            </strong>

                                                                        </div>


                                                                        <div>

                                                                            <span>
                                                                                JD
                                                                                Match
                                                                            </span>

                                                                            <strong>

                                                                                {
                                                                                    candidate.jd_match_score
                                                                                }

                                                                                /100

                                                                            </strong>

                                                                        </div>


                                                                        <div>

                                                                            <span>
                                                                                Final
                                                                                Score
                                                                            </span>

                                                                            <strong>

                                                                                {
                                                                                    candidate.final_score
                                                                                }

                                                                                /100

                                                                            </strong>

                                                                        </div>

                                                                    </div>

                                                                </div>

                                                            </td>

                                                        </tr>

                                                    )}

                                                </Fragment>

                                            )
                                        )}

                                    </tbody>

                                </table>

                            </div>

                        )}

                    </section>

                )}

            </main>

        </div>
    );
}

export default App;