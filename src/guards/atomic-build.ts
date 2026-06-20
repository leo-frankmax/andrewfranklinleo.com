import { mkdirSync, writeFileSync, existsSync, readdirSync, readFileSync, rmSync, statSync } from 'fs';
import { join, dirname } from 'path';

export interface AtomicBuildConfig {
  stagingDir: string;
  outputDir: string;
  trashDir: string;
}

export interface StagingValidation {
  valid: boolean;
  errors: string[];
}

export class AtomicBuild {
  private config: AtomicBuildConfig;

  constructor(config: AtomicBuildConfig) {
    this.config = config;
  }

  async initStaging(): Promise<void> {
    if (existsSync(this.config.stagingDir)) {
      rmSync(this.config.stagingDir, { recursive: true, force: true });
    }
    mkdirSync(this.config.stagingDir, { recursive: true });
  }

  async writeFileToStaging(relativePath: string, content: string): Promise<void> {
    const fullPath = join(this.config.stagingDir, relativePath);
    const dir = dirname(fullPath);
    if (!existsSync(dir)) {
      mkdirSync(dir, { recursive: true });
    }
    writeFileSync(fullPath, content, 'utf-8');
  }

  async validateStaging(options?: { requiredFiles?: string[] }): Promise<StagingValidation> {
    const errors: string[] = [];

    if (!existsSync(this.config.stagingDir)) {
      return { valid: false, errors: ['Staging directory does not exist'] };
    }

    const files = this.readdirRecursive(this.config.stagingDir, this.config.stagingDir);

    // Check for empty files
    for (const file of files) {
      const fullPath = join(this.config.stagingDir, file);
      const stat = statSync(fullPath);
      if (stat.size === 0) {
        errors.push(`Empty file: ${file}`);
      }
    }

    // Check required files
    if (options?.requiredFiles) {
      for (const required of options.requiredFiles) {
        if (!files.includes(required)) {
          errors.push(`Missing required file: ${required}`);
        }
      }
    }

    return { valid: errors.length === 0, errors };
  }

  async publish(): Promise<{ success: boolean; trashedFiles: string[] }> {
    const trashedFiles: string[] = [];

    // Trash old output
    if (existsSync(this.config.outputDir)) {
      if (!existsSync(this.config.trashDir)) {
        mkdirSync(this.config.trashDir, { recursive: true });
      }

      const existingFiles = this.readdirRecursive(this.config.outputDir, this.config.outputDir);
      for (const file of existingFiles) {
        const srcPath = join(this.config.outputDir, file);
        const destPath = join(this.config.trashDir, file);
        const destDir = dirname(destPath);
        if (!existsSync(destDir)) {
          mkdirSync(destDir, { recursive: true });
        }
        // Use copy + delete for cross-device support
        const content = readFileSync(srcPath);
        writeFileSync(destPath, content);
        rmSync(srcPath);
        trashedFiles.push(file);
      }
    }

    // Copy staging to output
    mkdirSync(this.config.outputDir, { recursive: true });
    const stagingFiles = this.readdirRecursive(this.config.stagingDir, this.config.stagingDir);
    for (const file of stagingFiles) {
      const srcPath = join(this.config.stagingDir, file);
      const destPath = join(this.config.outputDir, file);
      const destDir = dirname(destPath);
      if (!existsSync(destDir)) {
        mkdirSync(destDir, { recursive: true });
      }
      const content = readFileSync(srcPath, 'utf-8');
      writeFileSync(destPath, content, 'utf-8');
    }

    return { success: true, trashedFiles };
  }

  private readdirRecursive(dir: string, baseDir?: string): string[] {
    const base = baseDir || dir;
    const results: string[] = [];
    const entries = readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      const fullPath = join(dir, entry.name);
      const relativePath = fullPath.replace(base, '').replace(/^[/\\]/, '').replace(/\\/g, '/');
      if (entry.isDirectory()) {
        results.push(...this.readdirRecursive(fullPath, base));
      } else {
        results.push(relativePath);
      }
    }
    return results;
  }
}
