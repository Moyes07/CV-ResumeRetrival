import {React,useState} from "react";
import Header from "./components/Header";
import QueryGenerator from "./components/Query";

export default function App() {
  const [uploadDrawerOpen, setUploadDrawerOpen] = useState(false);

  return (
    <div>
      <Header onUploadClick={() => setUploadDrawerOpen(true)} />
      <QueryGenerator
        uploadDrawerOpen={uploadDrawerOpen}
        setUploadDrawerOpen={setUploadDrawerOpen}
      />
    </div>
  );
}
