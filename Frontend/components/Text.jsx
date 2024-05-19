import React, { useState } from 'react';

export function TextEditor() {
  const [text, setText] = useState('');
  const [positions, setPositions] = useState([]);
  const [dragging, setDragging] = useState(null);
  const [offset, setOffset] = useState({ x: 0, y: 0 });

  const handleTextChange = (e) => {
    setText(e.target.value);
  };

  const handleTextMouseDown = (index) => (e) => {
    e.preventDefault();
    setDragging(index);
    const offsetX = e.clientX - positions[index].x;
    const offsetY = e.clientY - positions[index].y;
    setOffset({ x: offsetX, y: offsetY });
  };

  const handleMouseMove = (e) => {
    if (dragging !== null) {
      const updatedPositions = [...positions];
      updatedPositions[dragging] = {
        x: e.clientX - offset.x,
        y: e.clientY - offset.y,
        text: positions[dragging].text,
      };
      setPositions(updatedPositions);
    }
  };

  const handleMouseUp = () => {
    if (dragging !== null) {
      setDragging(null);
      setOffset({ x: 0, y: 0 });
    }
  };

  const addText = () => {
    if (text) {
      setPositions([...positions, { x: 100, y: 100, text }]);
      setText('');
    }
  };

  return (
    <div>
      <div className='inputFeild'>
      <input
        type="text"
        value={text}
        onChange={handleTextChange}
        placeholder="Enter text"
      />
      </div>
      <button onClick={addText}>Add Text</button>
      <div
        className="page-container"
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
      >
        {positions.map((position, index) => (
          <div
            key={index}
            className="text-box"
            style={{
              position: 'absolute',
              top: position.y + 'px',
              left: position.x + 'px',
              zIndex: 1,
              cursor: dragging === index ? 'grabbing' : 'grab',
            }}
            onMouseDown={handleTextMouseDown(index)}
          >
            {position.text}
          </div>
        ))}
      </div>
    </div>
  );
}
