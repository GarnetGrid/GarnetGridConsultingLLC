"use client";
import { API_BASE } from "../constants";

import { useState, useEffect } from "react";

interface ImageData {
    id: number;
    filename: string;
    storage_path: string;
    description?: string;
    width: number;
    height: number;
    source_page?: number;
    source_url?: string;
}

interface LightboxProps {
    image: ImageData | null;
    onClose: () => void;
}

export default function Lightbox({ image, onClose }: LightboxProps) {
    useEffect(() => {
        const handleEscape = (e: KeyboardEvent) => {
            if (e.key === "Escape") {
                onClose();
            }
        };

        if (image) {
            document.addEventListener("keydown", handleEscape);
            document.body.style.overflow = "hidden";
        }

        return () => {
            document.removeEventListener("keydown", handleEscape);
            document.body.style.overflow = "unset";
        };
    }, [image, onClose]);

    if (!image) {
        return null;
    }

    return (
        <div className="lightboxOverlay" onClick={onClose}>
            <div className="lightboxContent" onClick={(e) => e.stopPropagation()}>
                <button className="lightboxClose" onClick={onClose} aria-label="Close">
                    ✕
                </button>

                <div className="lightboxImageWrapper">
                    <img
                        src={`${API_BASE}/images/${image.id}/file`}
                        alt={image.description || image.filename}
                        className="lightboxImage"
                    />
                </div>

                <div className="lightboxInfo">
                    <div className="lightboxFilename">{image.filename}</div>
                    {image.description && (
                        <div className="lightboxDescription">{image.description}</div>
                    )}
                    <div className="lightboxMeta">
                        <span>{image.width} × {image.height}</span>
                        {image.source_page && <span> • Page {image.source_page}</span>}
                    </div>
                </div>
            </div>
        </div>
    );
}
