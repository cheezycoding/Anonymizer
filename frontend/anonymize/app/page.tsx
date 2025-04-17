'use client';

import { useState } from 'react';

export default function Home() {
  // State to track the selected file
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  // State to track if we're currently processing a file
  const [isProcessing, setIsProcessing] = useState(false);
  // State to track any error messages
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  // State to track success status
  const [isSuccess, setIsSuccess] = useState(false);

  // This function will be called when the user selects a file
  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    // Clear any previous error messages
    setErrorMessage(null);
    setIsSuccess(false);
    
    // Get the selected file from the input element
    const file = event.target.files?.[0] || null;
    
    // If a file was selected, check if it's a PDF
    if (file) {
      if (file.type === 'application/pdf') {
        // If it's a PDF, update our state
        setSelectedFile(file);
      } else {
        // If it's not a PDF, show an error
        setErrorMessage('Please select a PDF file.');
        setSelectedFile(null);
      }
    }
  };

  // This function will be called when the user clicks the upload button
  const handleUpload = async () => {
    // Make sure we have a file to upload
    if (!selectedFile) {
      setErrorMessage('Please select a PDF file first.');
      return;
    }

    try {
      // Set processing state to true to show loading state
      setIsProcessing(true);
      setErrorMessage(null);
      
      // Create a FormData object to send the file
      const formData = new FormData();
      formData.append('file', selectedFile);
      
      // Get the API URL
      const apiUrl = process.env.NEXT_PUBLIC_API_URL;
      if (!apiUrl) {
         // Handle the case where the environment variable isn't set
         // Maybe throw an error or set a default (though throwing is safer)
         setErrorMessage("API URL is not configured. Please contact support.");
         setIsProcessing(false); // Make sure to stop processing
         return; // Stop the function
      }
      
      // Send the file to our backend API
      const response = await fetch(`${apiUrl}/anonymize`, {
        method: 'POST',
        body: formData,
      });
      
      // Check if the request was successful
      if (!response.ok) {
        // If not, get error details and show them
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to process the PDF');
      }
      
      // Get the response as a blob
      const blob = await response.blob();
      
      // Create a URL for the blob
      const url = window.URL.createObjectURL(blob);
      
      // Create a temporary link element
      const a = document.createElement('a');
      a.href = url;
      a.download = `anonymized_${selectedFile.name}`;
      document.body.appendChild(a);
      
      // Click the link to trigger the download
      a.click();
      
      // Clean up by removing the link
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      
      // Set success state
      setIsSuccess(true);
    } catch (error) {
      // Show any errors that occurred
      setErrorMessage(error instanceof Error ? error.message : 'An unknown error occurred');
    } finally {
      // Reset processing state
      setIsProcessing(false);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8 bg-gray-50">
      <div className="w-full max-w-2xl p-8 space-y-6 bg-white rounded-lg shadow-md">
        <h1 className="text-3xl font-bold text-center text-gray-800">
          PDF Anonymizer
        </h1>
        
        <p className="text-gray-600 text-center">
          Upload a PDF file to anonymize personally identifiable information (PII).
        </p>
        
        <div className="space-y-4">
          {/* File input section */}
          <div className="flex flex-col items-center justify-center w-full">
            <label htmlFor="file-upload" className="flex flex-col items-center justify-center w-full h-32 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100">
              <div className="flex flex-col items-center justify-center pt-5 pb-6">
                <p className="mb-2 text-sm text-gray-500">
                  <span className="font-semibold">Click to upload</span> or drag and drop
                </p>
                <p className="text-xs text-gray-500">PDF files only</p>
              </div>
              <input
                id="file-upload"
                type="file"
                accept="application/pdf"
                className="hidden"
                onChange={handleFileChange}
              />
            </label>
          </div>
          
          {/* Selected file info */}
          {selectedFile && (
            <div className="p-4 bg-blue-50 rounded-md">
              <p className="text-sm text-blue-800">
                Selected: <span className="font-medium">{selectedFile.name}</span>
              </p>
            </div>
          )}
          
          {/* Error message */}
          {errorMessage && (
            <div className="p-4 bg-red-50 rounded-md">
              <p className="text-sm text-red-800">{errorMessage}</p>
            </div>
          )}
          
          {/* Success message */}
          {isSuccess && (
            <div className="p-4 bg-green-50 rounded-md">
              <p className="text-sm text-green-800">
                PDF anonymized successfully! The download should start automatically.
              </p>
            </div>
          )}
          
          {/* Upload button */}
          <button
            onClick={handleUpload}
            disabled={!selectedFile || isProcessing}
            className={`w-full py-2 px-4 rounded-md text-white font-medium ${
              !selectedFile || isProcessing
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700'
            }`}
          >
            {isProcessing ? 'Processing...' : 'Anonymize PDF'}
          </button>
        </div>
      </div>
    </main>
  );
}
