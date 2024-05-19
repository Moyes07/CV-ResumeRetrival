import React from "react"

export default function Header() {
    return (
        <header className="header">
            <img 
                src="./images/BULOGO.jpeg" 
                className="header--image"
            />
            <h2 className="header--title">Bahria University CV Retrival</h2>
            <h4 className="header--project">Upload a CV</h4>
        </header>
    )
}