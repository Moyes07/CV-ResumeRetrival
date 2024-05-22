import React, { useState } from "react";

export default function QueryGenerator({ uploadDrawerOpen }) {
  const [inputs, setInputs] = useState([
    { category: "Experience", value: "" },
    { category: "Education", value: "" },
    { category: "Skills", value: "" },
  ]);
  const [pdfLinks, setPdfLinks] = useState([]); // State to store PDF links
  const [currentIndex, setCurrentIndex] = useState(0); // State to track the current PDF index
  const [drawerOpen, setDrawerOpen] = useState(false); // State to manage drawer open/close

  const handleInputChange = (index, event) => {
    const newInputs = [...inputs];
    newInputs[index].value = event.target.value;
    setInputs(newInputs);
  };


  const handleSelectChange = (index, event) => {
    const newInputs = [...inputs];
    newInputs[index].category = event.target.value;
    setInputs(newInputs);
  };

  const generateList = () => {
    return inputs
      .filter((input) => input.value.trim() !== "")
      .map((input) => [`${input.category}: ${input.value.trim()}`]);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    const resultList = generateList();
    console.log(resultList);

    try {
      const response = await fetch("http://127.0.0.1:5000/process_query", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ resultList }),
      });

      if (response.ok) {
        const responseData = await response.json();
        console.log("Success:", responseData);
        // Assuming responseData contains the URLs of the PDF files
        setPdfLinks(responseData.map((data) => data.pdf_link));
        setCurrentIndex(0); // Reset to first PDF
        setDrawerOpen(true); // Open the drawer
      } else {
        console.error("Error:", response.statusText);
      }
    } catch (error) {
      console.error("Error:", error);
    }
  };

  const handleNext = () => {
    setCurrentIndex((prevIndex) => (prevIndex + 1) % pdfLinks.length);
  };

  const handlePrev = () => {
    setCurrentIndex(
      (prevIndex) => (prevIndex - 1 + pdfLinks.length) % pdfLinks.length
    );
  };

  const handleUploadDrawer=()=>{
    setDrawerOpen(false)
  }

  function resetWindow() {
    window.location.reload();
  }

  return (
    <main>
      {pdfLinks.length === 0 ? (
        <form onSubmit={handleSubmit}>
          {inputs.map((input, index) => (
            <div className="container" key={index}>
              <select
                className="dropdown"
                value={input.category}
                onChange={(event) => handleSelectChange(index, event)}
              >
                <option value="Experience">Experience</option>
                <option value="Education">Education</option>
                <option value="Skills">Skills</option>
              </select>
              <input
                type="text"
                className="textbox"
                placeholder="Type here..."
                value={input.value}
                onChange={(event) => handleInputChange(index, event)}
              />
            </div>
          ))}
          <div className="getcvbuttondiv">
            <button className="getcvbutton" type="submit">
              Get CV
            </button>
          </div>
        </form>
      ) : (
        <div className={`drawer ${drawerOpen ? 'open' : ''}`} id="pdf-viewer">
          <div className="pdfheading">
            <h2 className="pdfheadingtext">CV PDF</h2>
            <button className="reset-button" onClick={resetWindow}>
              &times;
            </button>
          </div>
          <div className="embed-container">
            <embed
              src={pdfLinks[currentIndex]}
              type="application/pdf"
              width="100%"
              height="800px"
            />
          </div>
          <div className="navigation-buttons">
            <button
              className="getcvbutton"
              onClick={handlePrev}
              disabled={pdfLinks.length <= 1}
            >
              Previous
            </button>
            <button
              className="getcvbutton"
              onClick={handleNext}
              disabled={pdfLinks.length <= 1}
            >
              Next
            </button>
          </div>
        </div>
      )}

      <div className={`upload-drawer ${uploadDrawerOpen ? 'open' : ''}`}>
        <button className="close-button" onClick={resetWindow}>
          &times;
        </button>
        <h2>Upload CV</h2>
        <input type="file" accept=".pdf" />
        <button className="upload-button">Upload</button>
      </div>
    </main>
  );
}
