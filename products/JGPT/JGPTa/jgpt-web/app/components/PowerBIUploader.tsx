'use client';

import React, { useState } from 'react';

export default function PowerBIUploader() {
    const [file, setFile] = useState<File | null>(null);
    const [uploading, setUploading] = useState(false);
    const [result, setResult] = useState<any>(null);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setFile(e.target.files[0]);
        }
    };

    const handleUpload = async () => {
        if (!file) return;

        setUploading(true);
        setResult(null);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('http://localhost:8000/api/powerbi/prime', {
                method: 'POST',
                body: formData,
            });

            const data = await response.json();
            setResult(data);
        } catch (error) {
            console.error('Error uploading BIM:', error);
            setResult({ status: 'error', message: 'Upload failed.' });
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="p-4 border border-gray-700 rounded-lg bg-gray-800 text-gray-200">
            <h3 className="text-xl font-bold mb-4 text-[#FF4D00]">Power BI Model Primer</h3>
            <p className="mb-4 text-sm text-gray-400">
                Upload a <code>.bim</code> file (Table Editor export) to teach JGPT about your semantic model.
            </p>

            <div className="flex gap-4 items-center">
                <input
                    type="file"
                    accept=".bim,.json"
                    onChange={handleFileChange}
                    className="block w-full text-sm text-gray-400
            file:mr-4 file:py-2 file:px-4
            file:rounded-full file:border-0
            file:text-sm file:font-semibold
            file:bg-[#FF4D00] file:text-black
            hover:file:bg-[#cc3d00]"
                />
                <button
                    onClick={handleUpload}
                    disabled={!file || uploading}
                    className="bg-[#2a2a2a] hover:bg-[#333] text-white font-bold py-2 px-4 rounded border border-[#FF4D00] disabled:opacity-50"
                >
                    {uploading ? 'Priming...' : 'Prime Model'}
                </button>
            </div>

            {result && (
                <div className={`mt-4 p-3 rounded ${result.status === 'success' ? 'bg-green-900/50 border-green-500' : 'bg-red-900/50 border-red-500'} border`}>
                    <p className="font-mono text-sm">{result.message}</p>
                    {result.tables_detected && (
                        <div className="mt-2 text-xs text-gray-300">
                            <strong>Tables Learned:</strong> {result.tables_detected.join(', ')}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
