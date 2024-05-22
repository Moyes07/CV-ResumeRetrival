import React from "react";

export default function Header({ onUploadClick }) {
    const handleClick = () => {
        console.log("Clicked on 'Upload a CV' text");
        if (typeof onUploadClick === 'function') {
          onUploadClick();
        }
      };

  return (
    <header className="header">
      <img src="./images/BULOGO.jpeg" className="header--image" alt="Logo" />
      <h2 className="header--title">Bahria University CV Retrieval</h2>
      <h4 className="header--project" style={{ cursor: "pointer"}} onClick={handleClick}>
        Upload a CV
      </h4>
    </header>
  );
}
