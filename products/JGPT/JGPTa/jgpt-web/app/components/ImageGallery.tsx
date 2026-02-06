"use client";

import { useState } from "react";
import Image from "next/image";
import { API_BASE } from "../constants";

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

interface ImageGalleryProps {
    images: ImageData[];
    onImageClick?: (image: ImageData) => void;
}

export default function ImageGallery({ images, onImageClick }: ImageGalleryProps) {
    if (!images || images.length === 0) {
        return null;
    }

    return (
        <div className="imageGallery">
            <div className="galleryHeader">
                <span className="galleryIcon">🖼️</span>
                <span className="galleryTitle">Images ({images.length})</span>
            </div>
            <div className="galleryGrid">
                {images.map((img) => (
                    <div
                        key={img.id}
                        className="galleryItem"
                        onClick={() => onImageClick?.(img)}
                        title={img.description || img.filename}
                    >
                        <div className="imageWrapper">
                            <img
                                src={`${API_BASE}/images/${img.id}/file`}
                                alt={img.description || img.filename}
                                className="galleryImage"
                            />
                        </div>
                        {img.description && (
                            <div className="imageCaption">
                                {img.description.slice(0, 100)}
                                {img.description.length > 100 ? "..." : ""}
                            </div>
                        )}
                        {img.source_page && (
                            <div className="imageMeta">Page {img.source_page}</div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
}
